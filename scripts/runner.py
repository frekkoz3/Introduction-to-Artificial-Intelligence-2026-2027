"""This runner utility is linked to the Vacuum World environment"""
from scripts import *
from scripts.agent import Agent
import pygame
import sys
import gymnasium as gym

import multiprocessing as mp
from functools import wraps
from scripts.environment import VacuumWorld, RenderMode
from scripts.agent import Agent

def run_episode(env: gym.Env, agent: Agent, render: bool = True) -> float:
    """Run one episode and return the accumulated reward."""

    try:
        observation, info = env.reset()

        if render:
            env.render()

        total_reward = 0.0

        terminated = False
        truncated = False

        while not terminated and not truncated:

            action = agent.act(observation)

            observation, reward, terminated, truncated, info = env.step(action)

            if render:
                env.render()

            if env.window is not None:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        env.close()
                        truncated = True

            total_reward += reward

        return total_reward
    finally:
        env.close()

def human_testing(env: gym.Env):
    """Allows a human player to control the environment frame-by-frame."""
    assert env.render_mode == "human"

    done = False
    truncated = False

    KEY_MAP = {
        pygame.K_w: 0,  # UP
        pygame.K_s: 1,  # DOWN
        pygame.K_a: 2,  # LEFT
        pygame.K_d: 3,  # RIGHT
        pygame.K_e: 4,  # IDLE
        pygame.K_q: 5,  # SUCK
    }

    env.render()

    while not done and not truncated:
        action = 4

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                env.close()
                return

            if event.type == pygame.KEYDOWN:
                if event.key in KEY_MAP:
                    action = KEY_MAP[event.key]

        _, reward, done, truncated, info = env.step(action)

        env.render()

    env.close()

def evaluate(env, agent):
    pass

def train(env, agent):
    pass

def collect_trajectory(env, agent):
    pass

if __name__ == '__main__':
    
    from scripts.environment import VacuumWorld
    from scripts.agent import RandomAgent

    env = VacuumWorld()
    human_testing(env)