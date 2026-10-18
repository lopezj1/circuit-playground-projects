# Circuit Playground Projects

Short electronics projects for a parent and a 4-year-old, written in
CircuitPython. Each one fits in a 15-20 minute session and gives instant
feedback with lights, sound and touch. The kid picks the colors, sounds and
names; the grown-up types the code.

## The board: Circuit Playground Bluefruit

The [Circuit Playground Bluefruit](https://www.adafruit.com/product/4333) is a
round, kid-sized board from Adafruit with everything built in, so there's
nothing to solder:

- nRF52840 processor with Bluetooth Low Energy
- 10 color NeoPixel lights around the edge
- Speaker, microphone, light sensor and temperature sensor
- Accelerometer for shake, tilt and tap
- Buttons A and B, plus a slide switch
- Pads that respond to touch and fit alligator clips

It runs CircuitPython: the board shows up as a USB drive named `CIRCUITPY`,
and saving `code.py` to it restarts the program right away.

- Buy: [adafruit.com/product/4333](https://www.adafruit.com/product/4333)
- Docs: [Adafruit Circuit Playground Bluefruit guide](https://learn.adafruit.com/adafruit-circuit-playground-bluefruit)

This is **not** the Circuit Playground Express. Express examples often work,
but the pins, the touch pads (A1-A6 and TX here) and the setup differ.

## Setup

1. Install CircuitPython on the board (this repo uses 10.3.1). See the
   Adafruit guide above.
2. Install the libraries with circup (`pip install circup`):

   ```bash
   circup install adafruit_circuitplayground neopixel
   ```

   circup pulls in the libraries those depend on. If it says
   `Missing file boot_out.txt`, press reset once and try again.
3. The board mounts as `CIRCUITPY` on `D:`. If yours uses another drive letter,
   set `CIRCUITPY` (for example `export CIRCUITPY=/e`).

## Deploying

Usually you'll deploy the **launcher**, which puts every game on the board at
once:

```bash
./deploy.sh launcher
```

To work on one game by itself, deploy it by number or name instead:

```bash
./deploy.sh 01
```

From PowerShell (including the Claude desktop app's Terminal panel), use
`.\deploy launcher` or `.\deploy 01`. `deploy.cmd` runs `deploy.sh` through
Git Bash. The script only writes `.py` files and never deletes anything on the
board.

## Launcher controls

| Where | Do this | What happens |
|---|---|---|
| Menu | A | Next game (its color lights up, one pixel per game number) |
| Menu | B | Start the game |
| In a game | A+B together | Back to the menu |

Details and how to add a game: [launcher/README.md](launcher/README.md).

## Projects

| # | Project | Menu color | What it does |
|---|---|---|---|
| 00 | [hello](projects/00-hello) | (not in menu) | First test: buttons change colors, shake for a rainbow |
| 01 | [wand](projects/01-wand) | purple | Shake to cast spells, A picks the spell |
| 02 | [fruit-piano](projects/02-fruit-piano) | green | Touch pads (or fruit!) play notes |
| 03 | [dice](projects/03-dice) | yellow | Shake to roll, then count the lights |
| 04 | [halloween](projects/04-halloween) | pumpkin orange | Spooky jukebox with matching lights; shake for lightning, touch for BOO, cover for eyes |

The settings each kid can change (colors, sounds) are at the top of each
game's `game_*.py`.

## Repo layout

```
deploy.sh / deploy.cmd     copy code to the board (Git Bash / PowerShell)
shared/common.py           buttons, sound and menu-exit helpers for all games
launcher/code.py           the game menu
projects/NN-name/
  game_name.py             the game, with the kid's settings at the top
  code.py                  runs that game on its own
  README.md                controls, kid's choices, a session plan
```

## Troubleshooting

- **Green lights, `BOOT` drive shows up:** you double-tapped reset. Tap it once.
- **All lights red:** usually a USB cable or power problem. Try another cable.
- **Program doesn't seem to change:** make sure `CIRCUITPY` was found
  (`deploy.sh` says so), then press reset once.
