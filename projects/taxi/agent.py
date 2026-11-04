"""
    COPY THIS CODE INSIDE `submission.py` (IN THE SAME FOLDER AS THIS ONE).
    Remove this comment and add instead a line with written only:
        -`name`, `surname`, `student id`
    COMPLETE THE REQUIRED PARTS. YOU CAN CHANGE WHATEVER YOU LIKE, BUT:

    - you must mantain the definition of the methods as they are
    - you must use a search algorithm as the one seen in lectures to solve the task
    - you cannot use the optimal path as heuristic
    - you must describe your decision with comments here and there
    - you must not use only LLM / agents to solve the task. if you do it, we will know.

    The solution will be evaluated based on:

    - does your algorithm find a solution?
    - does your algorithm find the optimal solution (in terms of cumulative cost)
    - how much time does your algorithm take to find the solution?

    In order to obtain the maximum point finding the optimal solution is sufficient.
    The ones that do the best in terms of performances will get additional points.
"""
class Agent():

  def __init__(self, env): # DO NOT CHANGE THE DEFINITION
    self.env = env # this is an instance of TaxiWorld
    self.plan = []
    self.search()

  def act(self): # DO NOT CHANGE THE DEFINITION
    """Core function called from the runner in order to take an action."""
    # It is assumed that self.search has been already called
    if self.plan:
      return self.plan.pop(0)
    return 0 # Fallback

  def search(self): # DO NOT CHANGE THE DEFINITION
    """
    THIS IS THE METHOD YOU MUST IMPLEMENT.

    Core search routine to build the search tree and find a path to the goal.

    This method should populate self.plan.

    While using this method one should use the utilities of the environment for the search.

    We remember you:
        - is_goal(state)
        - get_possible_actions(state)
        - get_action_cost(state, action)
        - get_successor(state, action)
    You can read the implementation details directly in the environment.py of this folder.

    Notice, the utilities already assume the form of the state to be:

        (taxi_x, taxi_y, passenger_status, passenger_station, destination_station)
    
    The passenger_status can be:

        PASSENGER_WAITING
        PASSENGER_IN_TAXI
        PASSENGER_DELIVERED
    """
    self.plan = []
    pass