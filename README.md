# Brick Breaker

A brick breaker / Breakout clone built with pygame: multiple levels loaded
from JSON, two power-ups, and persisted high scores.

![status](https://img.shields.io/badge/tests-57%20passing-brightgreen)

## Why this exists

This started from a single-file pygame script
([avinashkranjan/Amazing-Python-Scripts](https://github.com/avinashkranjan/Amazing-Python-Scripts/tree/main/Brick%20Breaker%20game)).
Working through it turned up a few real issues:

- **A scoring system that was declared but never implemented.** The
  original had `score = 0` at module level and never incremented or
  displayed it anywhere. Scoring here is actually wired up end to end:
  `Brick.hit()` returns points, `GameState` accumulates them, and
  `scores.py` persists a per-level high score to disk between runs.
- **`Block = Block()` shadowed the class with an instance of itself**,
  which works but is a landmine for anyone importing `Block` later
  expecting the class.
- **Collision resolution used a fixed 5-pixel proximity threshold** to
  decide which side of a brick the ball hit. That's fragile: a fast ball
  can move more than 5px in one frame and land already overlapping a
  brick's corner, causing it to bounce the wrong way or tunnel through.
  This version instead compares how far the ball has penetrated the
  brick on each axis (`Rect.overlap` in `geometry.py`) and reflects off
  the axis with the smaller penetration - the axis it crossed first -
  which is correct regardless of ball speed. See
  `test_physics.py::TestReflectOffBrick`.
- **One hardcoded level, no tests.** Levels are now JSON files
  (`levels/*.json`), and all the actual game logic - collision, scoring,
  level transitions, power-ups, persistence - lives in modules with zero
  pygame dependency, so it's unit tested without a display.

## What's new

- **3 levels** with increasing difficulty, including unbreakable bricks
- **2 power-ups**: Wide Paddle and Slow Ball, each with a drop chance and
  a timed duration
- **Persisted high scores** per level, stored at `~/.brick_breaker/scores.json`
- **57 tests** covering physics, entities, level loading/validation,
  power-ups, score persistence, and full game-state transitions

## Installation

```bash
git clone <your-repo-url>
cd brick-breaker
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

```bash
python -m brick_breaker.game
```

Move with the arrow keys, click or press space to serve the ball. Clear
every breakable brick to advance to the next level; run out of lives and
it's game over. Power-ups drop occasionally when you destroy a brick.

## Running the tests

```bash
pytest
```

All game logic (`geometry.py`, `physics.py`, `entities.py`, `levels.py`,
`powerups.py`, `scores.py`, and `GameState` in `game.py`) has zero pygame
dependency and is tested directly. Only rendering and input handling
(`_draw`, `main`) touch pygame, and are intentionally kept thin.

## Project layout

```
levels/                     # JSON level definitions
src/brick_breaker/
├── geometry.py             # Rect type, no pygame dependency
├── physics.py              # collision resolution (pure functions)
├── entities.py             # Ball, Paddle, Brick
├── levels.py                # level loading + validation
├── powerups.py               # power-up specs and effects
├── scores.py                  # high score persistence
└── game.py                     # GameState (pure) + pygame rendering/input
tests/
├── test_physics.py
├── test_entities.py
├── test_levels.py
├── test_powerups.py
├── test_scores.py
└── test_game_state.py
```

## Attribution

Based on a brick breaker script from
[avinashkranjan/Amazing-Python-Scripts](https://github.com/avinashkranjan/Amazing-Python-Scripts),
used under its MIT license. This version fixes the collision-detection
and unused-score bugs described above, adds a level system, power-ups,
persisted scores, and a full test suite.

## License

MIT - see [LICENSE](LICENSE).
