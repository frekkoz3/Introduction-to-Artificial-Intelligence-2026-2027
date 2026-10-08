from abc import ABC, abstractmethod
from typing import Any

import gymnasium as gym

class Agent(ABC):
    """Base class for agents that will interact with Gymnasium environmet"""

    def __init__(self, env : gym.Env):
        """Setup the basic knowledge of the environment."""
        self.action_space = env.action_space
    
    @abstractmethod
    def act(self, observation: Any):
        """Choose an action given an observation."""
        raise NotImplementedError

class RandomAgent(Agent):
    """Random agent."""

    def __init__(self, env : gym.Env):
        """Just take the actions from the enviornment as basic knowledge"""
        self.action_space = env.action_space

    def act(self, observation: Any):
        """Observation are not actually used"""
        return self.action_space.sample()