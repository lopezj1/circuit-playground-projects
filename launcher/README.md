# Launcher

Every game on the board at once, so switching games doesn't need the computer.

```bash
./deploy.sh launcher
```

From PowerShell, use `.\deploy launcher` instead. This copies the menu, the
shared helper and every `projects/*/game_*.py`.

## Controls

| Where | Do this | What happens |
|---|---|---|
| Menu | A | Next game. The pixels show the game's color, one per game number |
| Menu | B | Start the game |
| In a game | A+B together | Back to the menu |

| # | Game | Color |
|---|---|---|
| 1 | [Wand](../projects/01-wand) | purple |
| 2 | [Fruit piano](../projects/02-fruit-piano) | green |
| 3 | [Dice](../projects/03-dice) | orange |

If a game crashes, the board flashes red, beeps low, and returns to the menu.
The error is printed to the serial console.

## How it works

- Games load only when started, and are unloaded with `gc.collect()` after
  A+B, so RAM is freed for the next one.
- Each game is a `game_*.py` module with a `run()` function that returns on
  A+B. `shared/common.py` provides `pressed()`, `wants_exit()`,
  `exit_held()` and `beep()`.
- After a game, the menu resets the lights and sound (brightness,
  `auto_write`, tone off), so games don't have to clean up after themselves.

## Adding a game

1. Make `projects/NN-name/` with a `game_name.py` that has a `run()`
   function. Copy an existing game as a starting point.
2. In the game loop, call `button = common.pressed()` and
   `if common.wants_exit(button): return`. In long animations, stop early
   when `common.exit_held()` is true.
3. Add a `code.py` that runs the game on its own:
   `from game_name import run` then `run()`.
4. Add one line to `GAMES` in `launcher/code.py` with its color and tone.
