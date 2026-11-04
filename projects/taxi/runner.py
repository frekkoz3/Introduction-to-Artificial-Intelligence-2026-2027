import pygame
import gymnasium as gym

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
        pygame.K_e: 4,  # PICKUP
        pygame.K_q: 5,  # DROPOFF
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

if __name__ == '__main__':
    from taxi.environment import *

    env = TaxiWorld(render_mode=RenderMode.HUMAN)

    human_testing(env)
