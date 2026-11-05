import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame
from enum import Enum


PASSENGER_WAITING = 0
PASSENGER_IN_TAXI = 1
PASSENGER_DELIVERED = 2

# '#' wall   '.' road   'r' residential   't' traffic   '$' toll
# 'P' passenger spawn (road)   'G' goal (road)
LAYOUT = [
    #0123456789ABCDE   (x)
    ".#...#.........",  # 0   
    ".#.###.#.#####.",  # 1
    "...#...#.#####.",  # 2
    ".###.#.#.#####.",  # 3
    "...#P#.#t#####.",  # 4   
    ".#.###.t.rr.r..",  # 5   
    ".#...#.#t#####.",  # 6
    ".#####.#r#####.",  # 7
    ".......#.......",  # 8
    "##############.",  # 9   
    "....rr...r.....",  # 10  
    ".##r##$########",  # 11  
    "......tt.......",  # 12 
    "#######t##r###.",  # 13  
    "G.rr.........r.",  # 14  
]

ACTIONS = {
    0: (0, -1),  # UP
    1: (0, 1),   # DOWN
    2: (-1, 0),  # LEFT
    3: (1, 0),   # RIGHT
}

ACTION_NAMES = {
    0: "UP",
    1: "DOWN",
    2: "LEFT",
    3: "RIGHT",
    4: "PICKUP",
    5: "DROPOFF",
}

TERRAIN_COSTS = {
    "road": 1,
    "residential": 3,
    "traffic": 5,
    "toll": 10,
}

TERRAIN_COLORS = {
    "road": (235, 235, 235),
    "residential": (190, 220, 190),
    "traffic": (245, 190, 120),
    "toll": (200, 180, 230),
}

WALL_COLOR = (65, 68, 75)
GRID_COLOR = (155, 155, 155)
TAXI_COLOR = (255, 205, 40)
RED = (220, 65, 65)
GREEN = (65, 180, 95)
TEXT_COLOR = (245, 245, 245)
BACKGROUND_COLOR = (35, 38, 44)


class RenderMode(Enum):
    HUMAN = "human"
    RGB_ARRAY = "rgb_array"


class ObservationType(Enum):
    GRID = "grid"
    IMAGE = "image"


class TaxiWorld(gym.Env):
    """
    Fixed-layout Taxi Grid World for BFS, UCS, and A*.

    State:
        (taxi_x, taxi_y, passenger_status, passenger_station,
         destination_station)

    passenger_status:
        PASSENGER_WAITING
        PASSENGER_IN_TAXI
        PASSENGER_DELIVERED

    Actions:
        0 = UP
        1 = DOWN
        2 = LEFT
        3 = RIGHT
        4 = PICKUP
        5 = DROPOFF
    """

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 10}

    def __init__(
        self,
        render_mode=RenderMode.HUMAN,
        observation_type=ObservationType.GRID,
        max_step=600,
        cell_size=56,
    ):
        super().__init__()

        self.grid_width = 15
        self.grid_height = 15
        self.cell_size = cell_size
        self.bar_height = 72
        self.max_step = max_step

        self.render_mode = (
            render_mode.value if isinstance(render_mode, RenderMode)
            else render_mode
        )
        self.observation_type = (
            observation_type.value
            if isinstance(observation_type, ObservationType)
            else observation_type
        )

        self.action_space = spaces.Discrete(6)

        self.stations = {
            0: {"name": "Red", "code": "R", "pos": (4, 4)},
            1: {"name": "Green", "code": "G", "pos": (0, 14)},
        }

        self.walls = set()
        self.terrain = {}
        self._generate_map()

        # Grid encoding:
        # 0=road, 1=wall, 2=station, 3=taxi,
        # 4=taxi with passenger, 5=residential,
        # 6=traffic, 7=toll.
        self.observation_space = spaces.Box(
            low=0,
            high=7,
            shape=(self.grid_height, self.grid_width),
            dtype=np.float32,
        )

        self.taxi = (0, 0)
        self.passenger_status = PASSENGER_WAITING
        self.passenger_loc = 0
        self.destination_loc = 1

        self.total_cost = 0
        self.total_step = 0
        self.score = 0
        self.route = []

        self.window = None
        self.canvas = None
        self.clock = None
        self.font = None
        self.small_font = None

        self._setup_window()
        self.reset()

    def _generate_map(self):
        """Create the map ."""
        symbol_to_terrain = {
            ".": "road", "P": "road", "G": "road",
            "r": "residential", "t": "traffic", "$": "toll",
        }

        self.walls = set()
        self.terrain = {}
        for y, row in enumerate(LAYOUT):
            for x, ch in enumerate(row):
                if ch == "#":
                    self.walls.add((x, y))
                else:
                    self.terrain[(x, y)] = symbol_to_terrain[ch]

        # In case a station ended up on a wall
        for station in self.stations.values():
            pos = station["pos"]
            self.terrain[pos] = "road"
            self.walls.discard(pos)

    # Search utilities 
    def get_state(self):
        """Return the complete, hashable state used by graph search."""
        return (
            self.taxi[0],
            self.taxi[1],
            self.passenger_status,
            self.passenger_loc,
            self.destination_loc,
        )

    def is_goal(self, state=None):
        """Goal: passenger delivered and taxi at the destination."""
        if state is None:
            state = self.get_state()

        tx, ty, status, _passenger_loc, destination_loc = state
        destination_pos = self.stations[destination_loc]["pos"]

        return (
            status == PASSENGER_DELIVERED
            and (tx, ty) == destination_pos
        )

    def get_possible_actions(self, state=None):
        """Return legal actions from a supplied or current state."""
        if state is None:
            state = self.get_state()

        tx, ty, status, passenger_loc, destination_loc = state
        legal = []

        # Movement actions.
        for action, (dx, dy) in ACTIONS.items():
            nx, ny = tx + dx, ty + dy

            if (
                0 <= nx < self.grid_width
                and 0 <= ny < self.grid_height
                and (nx, ny) not in self.walls
            ):
                legal.append(action)

        # Pickup: taxi must be at the waiting passenger's station.
        if status == PASSENGER_WAITING:
            passenger_pos = self.stations[passenger_loc]["pos"]
            if (tx, ty) == passenger_pos:
                legal.append(4)

        # Dropoff: taxi must be at the destination with passenger onboard.
        if status == PASSENGER_IN_TAXI:
            destination_pos = self.stations[destination_loc]["pos"]
            if (tx, ty) == destination_pos:
                legal.append(5)

        return legal

    def get_action_cost(self, state, action):
        """
        Return the positive cost of a legal action.

        Movement cost is the cost of the destination tile.
        Pickup and dropoff cost 1 each.
        Illegal actions have infinite search cost.
        """
        if action not in self.get_possible_actions(state):
            return float("inf")

        tx, ty, _status, _passenger_loc, _destination_loc = state

        if action in ACTIONS:
            dx, dy = ACTIONS[action]
            next_pos = (tx + dx, ty + dy)
            terrain_type = self.terrain[next_pos]
            return TERRAIN_COSTS[terrain_type]

        if action in (4, 5):
            return 1

        return float("inf")

    def get_successor(self, state, action):
        """
        Return the next state without mutating the live environment.

        Intended for BFS/UCS/A*. Raises ValueError for illegal actions.
        """
        if action not in self.get_possible_actions(state):
            raise ValueError(f"Illegal action {action} for state {state}")

        tx, ty, status, passenger_loc, destination_loc = state

        if action in ACTIONS:
            dx, dy = ACTIONS[action]
            return (
                tx + dx,
                ty + dy,
                status,
                passenger_loc,
                destination_loc,
            )

        if action == 4:  # Pickup
            return (
                tx,
                ty,
                PASSENGER_IN_TAXI,
                passenger_loc,
                destination_loc,
            )

        if action == 5:  # Dropoff
            return (
                tx,
                ty,
                PASSENGER_DELIVERED,
                passenger_loc,
                destination_loc,
            )

        raise ValueError(f"Unknown action {action}")

    # Gymnasium Interface
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.total_cost = 0
        self.total_step = 0
        self.score = 0
        self.route = []

        self.taxi = (0, 0)
        self.passenger_status = PASSENGER_WAITING
        self.passenger_loc = 0
        self.destination_loc = 1

        self.route.append(self.taxi)
        return self._get_obs(), self._get_info()

    def step(self, action):
        if not self.action_space.contains(action):
            raise ValueError(f"Invalid action: {action}")

        state = self.get_state()
        legal_actions = self.get_possible_actions(state)

        self.total_step += 1
        terminated = False
        truncated = False

        if action in legal_actions:
            cost = self.get_action_cost(state, action)
            next_state = self.get_successor(state, action)

            (
                tx,
                ty,
                self.passenger_status,
                self.passenger_loc,
                self.destination_loc,
            ) = next_state

            self.taxi = (tx, ty)
            reward = -float(cost)
            self.total_cost += cost
        else:
            # Invalid action: fixed penalty; state does not change.
            penalty = 5
            reward = -float(penalty)
            self.total_cost += penalty

        self.score += reward
        self.route.append(self.taxi)

        if self.is_goal():
            terminated = True

        if self.total_step >= self.max_step and not terminated:
            truncated = True

        return (
            self._get_obs(),
            reward,
            terminated,
            truncated,
            self._get_info(),
        )

    def _get_obs(self):
        grid = np.zeros(
            (self.grid_height, self.grid_width),
            dtype=np.float32,
        )

        terrain_codes = {
            "road": 0,
            "residential": 5,
            "traffic": 6,
            "toll": 7,
        }

        for (x, y), terrain_type in self.terrain.items():
            grid[y, x] = terrain_codes[terrain_type]

        for wx, wy in self.walls:
            grid[wy, wx] = 1

        for station in self.stations.values():
            sx, sy = station["pos"]
            grid[sy, sx] = 2

        tx, ty = self.taxi
        grid[ty, tx] = (
            4 if self.passenger_status == PASSENGER_IN_TAXI else 3
        )

        return grid

    def _get_info(self):
        return {
            "state": self.get_state(),
            "score": self.score,
            "total_cost": self.total_cost,
            "steps": self.total_step,
            "taxi_position": self.taxi,
            "passenger_status": self.passenger_status,
            "passenger_location": self.passenger_loc,
            "destination_location": self.destination_loc,
            "goal": self.is_goal(),
        }

    # Pygame Backbone for Visualization
    def _setup_window(self):
        if not pygame.get_init():
            pygame.init()
        if not pygame.display.get_init():
            pygame.display.init()
        if not pygame.font.get_init():
            pygame.font.init()

        if self.font is None:
            self.font = pygame.font.SysFont("Arial", 16, bold=True)
            self.small_font = pygame.font.SysFont("Arial", 12)

        width = self.grid_width * self.cell_size
        height = self.grid_height * self.cell_size

        if self.render_mode == "human":
            if self.window is None:
                self.window = pygame.display.set_mode((width, height))
                pygame.display.set_caption("Taxi Search World")
                self.clock = pygame.time.Clock()
        else:
            if self.canvas is None:
                self.canvas = pygame.Surface((width, height))

    def _passenger_status_text(self):
        if self.passenger_status == PASSENGER_WAITING:
            return "Waiting"
        if self.passenger_status == PASSENGER_IN_TAXI:
            return "In taxi"
        return "Delivered"

    def _render_frame(self):
        """
        Minimal renderer:
        - Plain colored grid cells
        - Taxi and station markers are simple squares
        - No text or status bar inside the grid
        """
        surface = self.window if self.render_mode == "human" else self.canvas
        surface.fill((245, 245, 245))

        cs = self.cell_size

        # Draw roads and walls.
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                rect = (x * cs, y * cs, cs, cs)

                if (x, y) in self.walls:
                    color = WALL_COLOR
                else:
                    terrain_type = self.terrain[(x, y)]
                    color = TERRAIN_COLORS[terrain_type]

                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, (190, 190, 190), rect, width=1)

        # Draw stations as simple colored squares.
        for idx, station in self.stations.items():
            sx, sy = station["pos"]
            inset = max(5, cs // 6)
            rect = (
                sx * cs + inset,
                sy * cs + inset,
                cs - 2 * inset,
                cs - 2 * inset,
            )

            color = RED if idx == 0 else GREEN
            pygame.draw.rect(surface, color, rect)

        # Draw taxi as a yellow square.
        tx, ty = self.taxi
        inset = max(8, cs // 4)
        taxi_rect = (
            tx * cs + inset,
            ty * cs + inset,
            cs - 2 * inset,
            cs - 2 * inset,
        )
        pygame.draw.rect(surface, TAXI_COLOR, taxi_rect)

        # When carrying the passenger, add a tiny dark marker.
        if self.passenger_status == PASSENGER_IN_TAXI:
            marker_size = max(4, cs // 8)
            marker_rect = (
                tx * cs + cs - marker_size - 3,
                ty * cs + 3,
                marker_size,
                marker_size,
            )
            pygame.draw.rect(surface, (35, 35, 35), marker_rect)

        return np.transpose(
            pygame.surfarray.array3d(surface),
            (1, 0, 2),
        ).astype(np.uint8)

    def render(self):
        if self.render_mode == "human":
            self._render_frame()
            pygame.display.flip()
            self.clock.tick(self.metadata["render_fps"])
            return True

        return self._render_frame()

    def close(self):
        if self.window is not None or self.canvas is not None:
            pygame.quit()
            self.window = None
            self.canvas = None
            self.clock = None


if __name__ == "__main__":
    env = TaxiWorld(render_mode=RenderMode.HUMAN)

    obs, info = env.reset()
    running = True

    while running:
        action = int(env.np_random.choice(env.get_possible_actions()))

        obs, reward, terminated, truncated, info = env.step(action)
        running = env.render()

        if terminated or truncated:
            print("Episode finished:", info)
            running = False

    env.close()
