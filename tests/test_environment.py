"""Run with: uv run --locked python -m unittest discover -s tests -v."""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pygame

from scripts.agent import Agent, RandomAgent
from scripts.environment import RESOURCES_PATH, VacuumWorld
from scripts.runner import run_episode
from scripts.setting import GameSetting


class EnvironmentTests(unittest.TestCase):
    def tearDown(self):
        pygame.quit()

    def test_observations_and_seed(self):
        for difficulty in (0, 1):
            for kind in ("grid", "image"):
                for mode in ("human", "rgb_array"):
                    with self.subTest(difficulty=difficulty, kind=kind, mode=mode):
                        env = VacuumWorld(difficulty=difficulty, observation_type=kind,
                                          render_mode=mode)
                        try:
                            first, info = env.reset(seed=12)
                            second, again = env.reset(seed=12)
                            np.testing.assert_array_equal(first, second)
                            self.assertEqual(info, again)
                            self.assertTrue(env.observation_space.contains(first))
                            self.assertEqual(first.dtype, np.float32 if kind == "grid" else np.uint8)
                            if kind == "grid":
                                self.assertEqual(first.shape, (env.setting.grid_height, env.setting.grid_width))
                                x, y = env.vacuum
                                self.assertEqual(first[y, x], 3.5 if env.vacuum in env.dirts else 3)
                                for x, y in env.walls:
                                    self.assertEqual(first[y, x], 2)
                                for x, y in env.dirts - {env.vacuum}:
                                    self.assertEqual(first[y, x], 1)
                            else:
                                self.assertEqual(first.shape, (env.setting.total_height, env.setting.width, 3))
                                self.assertGreater(first.max(), 1)
                            for action in range(6):
                                env.reset(seed=12)
                                observation, *_ = env.step(action)
                                self.assertTrue(env.observation_space.contains(observation))
                            self.assertTrue(env.observation_space.contains(env._get_obs(done=True)))
                            env.render()
                        finally:
                            env.close()

    def test_vacuum_on_dirt_observation(self):
        env = VacuumWorld(render_mode="rgb_array")
        self.addCleanup(env.close)
        env.vacuum = (2, 1)
        env.dirts = {env.vacuum}
        observation = env._get_obs()
        self.assertEqual(observation[1, 2], 3.5)
        self.assertTrue(env.observation_space.contains(observation))
        observation, reward, terminated, _, _ = env.step(5)
        self.assertEqual(observation[1, 2], 3)
        self.assertTrue(env.observation_space.contains(observation))
        self.assertTrue(terminated)
        self.assertEqual(reward, 110)

    def test_difficulty(self):
        for difficulty, dimensions, dirt in ((0, (4, 3), 1), (1, (10, 10), 10)):
            setting = GameSetting(difficulty)
            self.assertEqual((setting.grid_width, setting.grid_height), dimensions)
            self.assertEqual(setting.n_dirt, dirt)
        for difficulty in (-1, 2, 3, 99, None, "0"):
            for factory in (GameSetting, VacuumWorld):
                with self.subTest(difficulty=difficulty, factory=factory):
                    with self.assertRaisesRegex(ValueError, "Supported levels: 0 and 1"):
                        factory(difficulty=difficulty)

    def test_rewards_and_episode_end(self):
        env = VacuumWorld(render_mode="rgb_array", max_step=10)
        self.addCleanup(env.close)
        env.vacuum = (1, 1)
        env.dirts = {(2, 1)}
        for action, expected_reward, position in ((0, -3, (1, 1)), (4, -0.5, (1, 1)),
                                                  (5, -1, (1, 1)), (3, -0.1, (2, 1)),
                                                  (5, 110, (2, 1))):
            obs, reward, terminated, truncated, info = env.step(action)
            self.assertEqual(reward, expected_reward)
            self.assertEqual(env.vacuum, position)
            self.assertEqual(terminated, env.is_goal())
            self.assertFalse(truncated)
            self.assertTrue(env.observation_space.contains(obs))
        self.assertTrue(terminated)
        self.assertEqual(info["score"], 110)
        env.reset(seed=1)
        env.max_step = 1
        _, reward, terminated, truncated, _ = env.step(4)
        self.assertFalse(terminated)
        self.assertTrue(truncated)
        with self.assertRaises(ValueError):
            env.step(6)

    def test_agent_and_runner_cleanup(self):
        class UnfinishedAgent(Agent):
            def __init__(self, env):
                super().__init__(env)

            def act(self, observation):
                pass

        env = VacuumWorld(render_mode="rgb_array", observation_type="image", max_step=2)
        with self.assertRaises(TypeError):
            Agent(env)
        unfinished = UnfinishedAgent(env)
        self.assertIs(unfinished.action_space, env.action_space)
        with self.assertRaisesRegex(ValueError, "Invalid action None"):
            run_episode(env, unfinished, render=False)
        self.assertFalse(pygame.get_init())
        agent = RandomAgent(env)
        for _ in range(2):
            self.assertIsInstance(run_episode(env, agent, render=False), float)
            self.assertIsNone(env.canvas)
            self.assertFalse(pygame.get_init())
        env.close()  # Closing twice must also be safe.

    def test_assets_from_other_working_directory(self):
        original = Path.cwd()
        font = pygame.font.Font
        with tempfile.TemporaryDirectory() as directory:
            try:
                os.chdir(directory)
                with patch("pygame.font.Font", wraps=font) as load_font:
                    env = VacuumWorld(render_mode="rgb_array")
                self.addCleanup(env.close)
                self.assertEqual(Path(load_font.call_args.args[0]), RESOURCES_PATH / "font/minecraft/Minecraft.ttf")
                self.assertTrue(Path(load_font.call_args.args[0]).is_file())
                # The repository has no component sprites: verify the fallback floor.
                self.assertEqual(env.floor_background.get_at((36, 36))[:3], (180, 180, 180))
                # A synthetic sprite checks tiling of the non-square level 0 grid.
                sprite = pygame.Surface((35, 35))
                sprite.fill((12, 34, 56))
                env.sprites["component_floor"] = sprite
                env.walls = set()
                env._blit_background()
                self.assertEqual(env.floor_background.get_at((139, 104))[:3], (12, 34, 56))
            finally:
                os.chdir(original)


if __name__ == "__main__":
    unittest.main()
