import pygame
import gymnasium as gym

from taxi.agent import Agent
from taxi.environment import RenderMode
from time import perf_counter

def run(env: gym.Env, agent : Agent):

    cumulative_cost = 0
    steps = 0
    done = False
    truncated = False

    summary = {
                "solution" : False, 
                "cost" : float("inf"),
                "steps" : float("inf"),
                "optimal_solution" : False,
                "search_time" : float("inf")
               }

    env.render()

    obs = env.get_state()

    t0 = perf_counter()
    rep = 10    
    for r in range(rep):
        agent.search()
    t1 = perf_counter()

    summary["search_time"] = (t1-t0)/rep

    while not done and not truncated:

        if env.render_mode == RenderMode.HUMAN:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    env.close()
                    return summary

        action = agent.act()
        steps += 1
        obs, reward, done, truncated, info = env.step(action)
        cumulative_cost += (-reward)
        
        env.render()

    summary["steps"] = steps
    summary["cost"] = cumulative_cost
    summary["solution"] = not truncated
    summary["optimal_solution"] = (cumulative_cost == 71)

    env.close()
    
    return summary

if __name__ == '__main__':
    from taxi.submission import Agent
    from taxi.environment import TaxiWorld
    env = TaxiWorld()
    agent = Agent(env)
    summary = run(env, agent)
    print(summary)