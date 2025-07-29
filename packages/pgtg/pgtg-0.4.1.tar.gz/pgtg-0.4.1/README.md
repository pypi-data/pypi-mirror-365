# ProcGrid Traffic Gym (pgtg)

A driving simulation on a grid with procedural generated maps and traffic. Compatible with the Gymnasium API standard.

### Installation

```bash
pip install pgtg
```

### Usage
The easiest way to use pgtg is to create the environment with gymnasium:
```python
import pgtg
env = gymnasium.make("pgtg-v2")
```
The package relies on ```import``` side-effects to register the environment
name so, even though the package is never explicitly used, its import is
necessary to access the environment.  

If you want to access the environment constructor directly this is also possible:
```python
from pgtg import PGTGEnv
env = PGTGEnv()
```

## Environment
ProcGrid Traffic Gym procedurally generates a map consisting of multiple preconstructed tiles or loads a map from a file. The goal is to drive from the start of the map to the end. The navigation task is not part of this environment, instead a shortest path is provided and marked on the map.  

The environment is highly customizable, see the environment constructor for more info.

### Action Space
ProcGrid Traffic Gym has a `Discrete(9)` action space.

| Value | Meaning                   |
|-------|---------------------------|
| 0     | accelerate left and up    |
| 1     | accelerate left           |
| 2     | accelerate left and down  |
| 3     | accelerate up             |
| 4     | don't accelerate          |
| 5     | accelerate down           |
| 6     | accelerate right and up   |
| 7     | accelerate right          |
| 8     | accelerate right and down |

### Observation Space
ProcGrid Traffic Gym has a `Dict` observation space that shows the 9x9 area the agent currently is inside or, if a sliding observation window is used, a area of the specified size centered on the agent.
| Key | Type | Explanation |
|-----|------|-------------|
| "position" | `MultiDiscrete` | The x and y position of the agent within the observation window or, if a sliding observation window is used, always `(0, 0)`. |
| "velocity" | `Box` | The velocity of the agent in x and y direction. |
| "map" | `Dict` | The current observation window. The keys are the name of the features (`"walls"`, `"goals"`, `"ice"`, `"broken road"`, `"sand"`, and `"traffic"`). Each item is a `MultiBinary` that encodes that feature as a hot one encoding. |
| "next_subgoal_direction" | `Discrete(5)` | The direction of the next subgoal or `-1` if there is no next subgoal (most likely because the agent took a wrong turn). __This is disabled by default. It can be enabled with the `use_next_subgoal_direction` argument of the environment constructor.__|

Most reinforcement learning implementations can't deal with `Dict` observations directly, thus it might be necessary to flatten the observations. This is easily doable with the `gymnasium.wrappers.FlattenObservation` wrapper:
```python
from gymnasium.wrappers import FlattenObservation
env = FlattenObservation(env)
```

### Reward
Crossing a subgoal is rewarded with `+100 / number of subgoals` as is finishing the whole map. Moving into a wall or traffic is punished with `-100` and ends the episode. Standing still or moving to a already visited position can also penalized but is not per default. The reward values for each of this can be customized.

### Render modes
| Name | Explanation |
|------|-------------|
| human | `render()` returns `None` but a pygame window showing the environment is opened automatically when `step()` is called. |
| rgb_array | `render()` returns a `np.array` representing a image. |
| pil_image| `render()` returns a `PIL.Image.Image`, useful for displaying inside jupiter notebooks. |

### Obstacles
| Name | Effect |
|------|--------|
| Ice | When driving over a square with ice, there is a chance the agent moves in a random direction instead of the expected one. |
| Sand | When driving over sand, there is a chance that the agent is slowed, as the velocity is reset to 0. |
| Broken road | When driving over broken road, there is a chance for the agent to get a flat tire. This slows the agent down, as the velocity is reset to 0 every step. A flat tire lasts until the end of the episode.|

## Version History
### v0.1.0
- initial release
### v0.2.0
- Sand now slows down with a customizable probability (default 20%) instead of always.
- Bump environment version to v1 because the changes impact reproducibility with earlier versions.
### v0.3.0
- The x and y coordinates of observations are no longer swapped. This was the case for historical reasons but serves no use any more.
- Adds the option to use a sliding observation window of variable size.
- Adds the option to use the direction of the next subgoal as a additional observation.
- Bump environment version to v2 because the changes impact reproducibility with earlier versions.
### v0.3.1
- Fix bug that made it impossible to save a map as a file.
### v0.4.0
- Adds the option to have the start and goal of a map at custom or random positions.
- Bump environment version to v3 because the changes impact reproducibility with earlier versions.
- Update dependencies to allow for use with python versions ^3.10.