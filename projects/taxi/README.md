# Taxi Grid World — Search Algorithms Project

Welcome to the **Taxi Grid World** assignment! In this project, you will implement search algorithms (such as Uninformed Search and $A^*$ Search) with various heuristics to find the **cheapest route** for a taxi driver. Your goal is to navigate from a starting position to pick up a passenger and deliver them to their target destination with minimal path cost.

---

## Overview & Problem Definition

The environment represents a grid city map containing obstacles (walls), varying terrain types, a passenger pickup location, and a final dropoff location.

Your task is divided into two phases:

1. **Pickup Phase:** Drive from the initial taxi location to the passenger station and perform the `PICKUP` action.
2. **Delivery Phase:** Transport the passenger from the pickup location to their destination station and perform the `DROPOFF` action.

The goal is achieved when the passenger is successfully delivered and the taxi stands at the final destination.

---

## State Representation

To apply graph search algorithms like BFS, Uniform Cost Search (UCS), or $A^*$, you need to track state transitions. The state in `TaxiWorld` is represented as a 5-tuple:

$$\text{State} = (x, y, \text{status}, \text{passenger\_loc}, \text{destination\_loc})$$

- **$x, y$**: Current grid coordinates of the taxi (0-indexed).
- **$\text{status}$**: Current status of the passenger:
  - `0`: `PASSENGER_WAITING` (waiting at pickup)
  - `1`: `PASSENGER_IN_TAXI` (in transit)
  - `2`: `PASSENGER_DELIVERED` (at destination)
- **$\text{passenger\_loc}$**: Index of the passenger's pickup station (`0` = Red Station).
- **$\text{destination\_loc}$**: Index of the destination station (`1` = Green Station).

---

## Actions & Movement Costs

The action space consists of 6 discrete actions:

| Action ID | Action Name | Description | Base Cost |
| :---: | :---: | :--- | :---: |
| `0` | `UP` | Move up 1 cell | Terrain-dependent |
| `1` | `DOWN` | Move down 1 cell | Terrain-dependent |
| `2` | `LEFT` | Move left 1 cell | Terrain-dependent |
| `3` | `RIGHT` | Move right 1 cell | Terrain-dependent |
| `4` | `PICKUP` | Pick up passenger at station | `1` |
| `5` | `DROPOFF` | Drop off passenger at destination | `1` |

### Terrain Costs

Different grid cells incur different traverse costs:

| Symbol | Terrain Type | Color in Render | Cost ($g(n)$ impact) |
| :---: | :--- | :--- | :---: |
| `.` | Road | Light Gray | `1` |
| `r` | Residential Area | Light Green | `3` |
| `t` | Traffic Zone | Light Orange | `5` |
| `$` | Toll Gate | Light Purple | `10` |
| `#` | Wall | Dark Gray | Impassable |

> **Note:** The step reward returned by `env.step(action)` is the negative action cost ($R = -c$). An illegal move incurs a penalty cost of $5$ and leaves the state unchanged.

---

## Key Environment Methods for Search

You can interface with the environment directly through built-in helper methods designed specifically for search algorithms without mutating the live state:

### State and Action Methods

- `env.get_state()`: Returns the current state tuple.
- `env.is_goal(state=None)`: Checks if the given state (or current state) satisfies the goal condition.
- `env.get_possible_actions(state=None)`: Returns a list of legal actions available from the specified state.
- `env.get_action_cost(state, action)`: Returns the transition cost of executing `action` from `state`. Returns `inf` for illegal actions.
- `env.get_successor(state, action)`: Returns the resulting **next state** tuple after taking `action` from `state` (does **not** alter the actual environment).

### Station Locations

You can access station coordinates via `env.stations`:

- **Red Station (Pickup):** `env.stations[0]["pos"]` $\rightarrow (4, 4)$
- **Green Station (Dropoff):** `env.stations[1]["pos"]` $\rightarrow (0, 14)$

---

## Example

Here is a simple example showing how to "play" the game using `WASD` and `EQ` as keys for movements and for pipckup and dropoff (look directly at the code in `taxi\runner.py` for more references).

```bash
cd projects
py -m taxi.runner
```

Use this example just to explore the environment and think about how to solve the problem within the search framework.

---

## Your work

You must implement a file named `submsission.py` where you implement an agent (following the structure present in `agent.py`). In order to make it easier for you, you can literally copy and paste the code in `agent.py` to begin with. Later modified where needed!

**It is important that you add** your `name` `surname` and `student id` in the header of the file (first line in the format NAME SURNAME STUDENT-ID). Later you will upload the file to Teams.

You can test your submission running

```bash
cd projects
py -m taxi.test
```

You will obtain a summary with the target metrics for the assignment.
