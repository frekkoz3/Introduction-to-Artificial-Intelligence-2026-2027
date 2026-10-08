import gymnasium as gym
from gymnasium import spaces
from scripts import *
from pathlib import Path
import numpy as np
import pygame

from scripts.setting import *

RESOURCES_PATH = Path(__file__).resolve().parent / "resources"
SEED = 0

class VacuumWorld(gym.Env):
    """
    Simple grid-world vacuum cleaner environment.

    The environment contains:
        - a vacuum cleaner
        - walls
        - dirt cells

    Actions:
        0 = UP
        1 = DOWN
        2 = LEFT
        3 = RIGHT
        4 = IDLE
        5 = SUCK

    The goal is to clean every dirty cell.

    Coordinates
    -----------
    We consistently use (x, y):

        x -> column -> left/right
        y -> row    -> up/down

    Thus:
        (0, 0) = top-left cell

    For numpy arrays, the conversion is:

        grid[y, x]
    """

    def __init__(self, render_mode=RenderMode.HUMAN, observation_type=ObservationType.GRID, max_step=600, difficulty=0, n_obstacles=10, n_dirt=1, **kwargs):
    
        super().__init__()

        self.setting = GameSetting(difficulty)

        self.metadata = {
                "render_modes": ["human", "rgb_array"],
                "render_fps": self.setting.fps,
            }

        # Convert Enum -> string if necessary
        if isinstance(render_mode, RenderMode):
            render_mode = render_mode.value

        if isinstance(observation_type, ObservationType):
            observation_type = observation_type.value

        if render_mode not in self.metadata["render_modes"]:
            raise ValueError(
                f"Invalid render_mode: {render_mode}. "
                f"Expected one of {self.metadata['render_modes']}"
            )

        if observation_type not in {"grid", "image"}:
            raise ValueError(
                f"Invalid observation_type: {observation_type}"
            )

        self.render_mode = render_mode
        self.observation_type = observation_type

        self.max_step = max_step
        self.difficulty = difficulty

        self.n_obstacles = n_obstacles
        self.n_dirt = n_dirt

        self.status_bar = self.setting.status_bar

        self.action_space = spaces.Discrete(6) # 0=UP, 1=DOWN, 2=LEFT, 3=RIGHT, 4=IDLE, 5=SUCK

        if self.observation_type == ObservationType.IMAGE :
            self.observation_space = spaces.Box(
                low=0, high=255, shape=(self.setting.total_height, self.setting.width, 3), dtype=np.uint8
            )
        else:
            # 0 = clean floor
            # 1 = dirt
            # 2 = wall
            # 3 = vacuum, 3.5 = vacuum on dirt
            self.observation_space = spaces.Box(
                low=0, high=4, shape=(self.setting.grid_height, self.setting.grid_width), dtype=np.float32
            )

        self.window = None
        self.canvas = None
        self.clock = None
        self.font = None

        self.sprites_loaded = False
        self.floor_background = None

        self.vacuum = (1, 1)
        self.direction = (0, 1)

        self.walls = set()
        self.dirts = set()

        self.score = 0
        self.total_step = 0

        self.explored_states = []
        self.route = []

        self._setup_window()
        self._load_and_scale_sprites()  

        self.reset()

    def _setup_window(self):

        """Initialize Pygame and the correct render mode."""
        if not pygame.get_init():
            pygame.init()
        if not pygame.display.get_init():
            pygame.display.init()
        if not pygame.font.get_init():
            pygame.font.init()

        if self.window is not None or self.canvas is not None:
            return

        font_path = RESOURCES_PATH / "font" / "minecraft" / "Minecraft.ttf"
        
        try:
            self.font = pygame.font.Font(font_path, 16)
        except FileNotFoundError:
            self.font = pygame.font.SysFont("Arial", 24, bold=True)
        
        if self.render_mode == "human":
            self.window = pygame.display.set_mode((self.setting.width, self.setting.total_height))
            pygame.display.set_caption("Vaccum Environment")
            self.clock = pygame.time.Clock()
        else:
            try:
                self.canvas = pygame.display.set_mode((self.setting.width, self.setting.total_height), pygame.HIDDEN)
            except pygame.error:
                self.canvas = pygame.display.set_mode((self.setting.width, self.setting.total_height))

    def _load_and_scale_sprites(self):
        """Loads assets and resizes them to match the environment's CELL_SIZE."""

        def load_sp(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (self.setting.cell_size, self.setting.cell_size))
            except FileNotFoundError:
                return None
        
        if not self.sprites_loaded:

            """Once defined the structure we can work on this"""
            self.sprites = {}
            components = ["cleaner", "dirt", "floor"]

            for comp in components:
                self.sprites[f"component_{comp}"] = load_sp(RESOURCES_PATH / "components" / f"{comp}.png")

            self.sprites_loaded = True

    def _generate_map(self):
        """Generate a random map of the house to clean"""
        self.walls = set()
        self.dirts = set()

        if self.difficulty == 0 or self.difficulty == 1:
            # Vertical wall dividing the house into two rooms.
            wall_x = self.setting.grid_width // 2

            # Leave one doorway in the middle.
            doorway_y = self.setting.grid_height // 2

            for y in range(self.setting.grid_height):
                if y != doorway_y:
                    self.walls.add((wall_x, y))

            # Walls all around
            for x in range (self.setting.grid_width):
                for y in range (self.setting.grid_height):
                    if x == 0 or x == (self.setting.grid_width - 1) or y == 0 or y == (self.setting.grid_height - 1):
                        self.walls.add((x, y))
    
        elif self.difficulty == 2:
            pass
        else:
            pass

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self._setup_window()

        self.score = 0
        self.total_step = 0

        self.explored_states = []
        self.route = []

        self._generate_map()

        valid_cells = [(x, y) for x in range(self.setting.grid_width) for y in range(self.setting.grid_height) if (x, y) not in self.walls]

        # if difficulty > 0 : also obsttacles to take in account

        if not valid_cells: # debug
            raise RuntimeError(
                "Map generation produced no valid cells."
            )

        vacuum_index = self.np_random.integers(len(valid_cells))

        self.vacuum = valid_cells[vacuum_index]

        self.direction = (0, -1)

        dirt_candidates = valid_cells
        
        number_of_dirt = min(self.setting.n_dirt, len(dirt_candidates))

        if number_of_dirt > 0:
            dirt_indices = self.np_random.choice(len(dirt_candidates), size=number_of_dirt, replace=False)
            self.dirts = {dirt_candidates[int(i)] for i in np.atleast_1d(dirt_indices)}
        else:
            self.dirts = set()

        self._blit_background(reset=True)

        observation = self._get_obs()
        info = self._get_info()

        return observation, info


    def _blit_background(self, reset = True):

        if reset or self.floor_background is None: # Setting for the first time everything
            self.floor_background = pygame.Surface((self.setting.width, self.setting.height))
            # render the house layout (without dirts or anything)
            floor_sprite = self.sprites["component_floor"]
            for x in range(self.setting.grid_width):
                for y in range(self.setting.grid_height):
                    position = (x * self.setting.cell_size, y * self.setting.cell_size)
                    if floor_sprite is not None:
                        self.floor_background.blit(floor_sprite, position)
                    else:
                        pygame.draw.rect(self.floor_background, (180, 180, 180), (*position, self.setting.cell_size, self.setting.cell_size))

            for x, y in self.walls:
                position = (x * self.setting.cell_size, y * self.setting.cell_size)
                pygame.draw.rect(self.floor_background, (50, 50, 50), (*position, self.setting.cell_size, self.setting.cell_size))
                pygame.draw.rect(self.floor_background, (20, 20, 20), (*position, self.setting.cell_size, self.setting.cell_size), width=2)   

    def _get_obs(self, done = False):
        # Terminal observations use the same representation as other states.
        if self.observation_type == ObservationType.IMAGE:
            frame = self._render_frame()
            return frame
        else:
            # the grid is done such that
            # 0 stands for clean floor
            # 1 stands for dirty floor
            # 2 stands for wall
            # 3 stands for vacuum cleaner, 3.5 for vacuum cleaner on dirt
            # other numbers will stand for other things
            grid = np.zeros((self.setting.grid_height, self.setting.grid_width), dtype=np.float32)

            for x, y in self.dirts:
                grid[y, x] = 1

            for x, y in self.walls:
                grid[y, x] = 2
            
            x, y = self.vacuum
            grid[y, x] = 3
            if self.vacuum in self.dirts:
                grid[y, x] = 3.5 # special case


            return grid

    def _get_info(self):

        return {
            "score": self.score,
            "steps": self.total_step,
            "vacuum_position": self.vacuum,
            "dirt_remaining": len(self.dirts),
            "goal": self.is_goal(),
        }

    def _get_rotation_angle(self, vector):
        """Utility used to determine the rotation of the sprite"""
        mapping = {(0, -1): 0, (-1, 0): 90, (0, 1): 180, (1, 0): 270}
        return mapping.get(vector, 0)

    def is_goal(self):
        """Return True if the entire house is clean."""

        return len(self.dirts) == 0
    
    def get_possible_actions(self, action = None):
        """
        Return the actions that are legal from the
        current vacuum position.

        If action is provided return if it legal or not

        This is useful for search algorithms.
        """
        x, y = self.vacuum
        possible = {
            0: (x, y - 1),  # UP
            1: (x, y + 1),  # DOWN
            2: (x - 1, y),  # LEFT
            3: (x + 1, y),  # RIGHT
            4: (x, y),      # IDLE
            5: (x, y),      # SUCK
        }
        legal = []
        for candidate_action, position in possible.items():
            if candidate_action in (4, 5): # you can always idle and suck
                legal.append(candidate_action)
                continue

            new_x, new_y = position

            if (0 <= new_x < self.setting.grid_width and 0 <= new_y < self.setting.grid_height and (new_x, new_y) not in self.walls):
                legal.append(candidate_action)

        if action is None:
            return legal
        
        return action in legal

    def get_score(self):
        return self.score

    def step(self, action):

        if not self.action_space.contains(action):
            raise ValueError(f"Invalid action {action}")

        self.total_step += 1

        reward = -1
        terminated = False
        truncated = False

        old_position = self.vacuum

        directions = {
            0: (0, -1),  # UP
            1: (0, 1),   # DOWN
            2: (-1, 0),  # LEFT
            3: (1, 0),   # RIGHT
        }

        if action in directions:
            dx, dy = directions[action]

            new_position = (self.vacuum[0] + dx, self.vacuum[1] + dy)

            if self.get_possible_actions(action):
                self.vacuum = new_position
                self.direction = (dx, dy)
                reward = -0.1

            else:
                reward = -3.0

        elif action == 4:
            reward = -0.5

        elif action == 5:
            if self.vacuum in self.dirts:
                self.dirts.remove(self.vacuum)
                reward = 10
                self.score += 10
            else:
                reward = -1

        if self.is_goal():
            terminated = True
            reward += 100
            self.score += 100

        if self.total_step >= self.max_step:
            truncated = True

        self.route.append(self.vacuum)
        _ = old_position

        observation = self._get_obs()
        info = self._get_info()

        return (observation, reward, terminated, truncated, info)
    
    def _render_frame(self):
        """Internal worker function that draws the frame onto the canvas."""

        paint_surface = self.window if self.render_mode == "human" else self.canvas
        paint_surface.fill((40, 40, 40))

        if self.status_bar:
        
            total_seconds = self.total_step // self.metadata["render_fps"]
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            time_str = f"{minutes:02d}.{seconds:02d}"

            diff_text = self.font.render(f"Difficulty {self.difficulty}", True, (255, 255, 255))
            score_text = self.font.render(f"Score {self.score}", True, (255, 215, 0))
            time_text = self.font.render(f"Time {time_str}", True, (255, 255, 255))
            
            text_y = (self.setting.bar_height - diff_text.get_height()) // 2
            paint_surface.blit(diff_text, (20, text_y))
            paint_surface.blit(score_text, (self.setting.width // 2 - score_text.get_width() // 2, text_y))
            paint_surface.blit(time_text, (self.setting.width - time_text.get_width() - 20, text_y))

        # Floor background + walls
        paint_surface.blit(self.floor_background, (0, self.setting.bar_height))

        dirt_sprite = self.sprites["component_dirt"]

        # Dirts
        for x, y in self.dirts:
            screen_pos = (x * self.setting.cell_size, y * self.setting.cell_size + self.setting.bar_height)
            if dirt_sprite is not None:
                paint_surface.blit(dirt_sprite, screen_pos)
            else:
                pygame.draw.circle(paint_surface, (100, 70, 30), ( x * self.setting.cell_size + self.setting.cell_size // 2,  y * self.setting.cell_size + self.setting.bar_height + self.setting.cell_size // 2), self.setting.cell_size // 4)

        # Vacuum cleaner
        x, y = self.vacuum
        screen_pos = (x * self.setting.cell_size, y * self.setting.cell_size + self.setting.bar_height)
        vacuum_sprite = self.sprites["component_cleaner"]
        if vacuum_sprite is not None:
            angle = self._get_rotation_angle(self.direction)
            rotated_vacum = pygame.transform.rotate(vacuum_sprite, angle)
            paint_surface.blit(rotated_vacum, screen_pos)
        else:
            pygame.draw.circle(paint_surface, (40, 100, 220), ( x * self.setting.cell_size + self.setting.cell_size // 2,  y * self.setting.cell_size + self.setting.bar_height + self.setting.cell_size // 2), self.setting.cell_size // 3)

        img_array = pygame.surfarray.array3d(paint_surface)

        # pygame gives:
        #   width x height x channels
        #
        # Gymnasium expects:
        #   height x width x channels

        frame = np.transpose(img_array, (1, 0, 2))

        return frame.astype(np.uint8)
    
    def render(self):
        if self.render_mode == "human":
            if not pygame.get_init() or not pygame.display.get_init():
                self._setup_window()

        frame = self._render_frame()

        if self.render_mode == "rgb_array":
            return frame

        if self.render_mode == "human":
            pygame.display.flip()
            self.clock.tick(self.metadata["render_fps"])
            return True

    def close(self):
        if self.window or self.canvas:
            pygame.quit()
            self.window = None
            self.canvas = None
            self.clock = None

if __name__ == '__main__':

    env = VacuumWorld(
        render_mode=RenderMode.HUMAN,
        observation_type=ObservationType.GRID,
        difficulty=0,
    )

    observation, info = env.reset(seed=SEED)

    print("Initial observation:")
    print(observation)

    print()
    print("Initial info:")
    print(info)

    running = True

    while running:

        action = env.action_space.sample()

        observation, reward, terminated, truncated, info = env.step(action)

        running = env.render()

        if terminated or truncated:
            print("Episode finished.")
            print(info)
            running = False
            #observation, info = env.reset(seed=SEED)

    env.close()