# cpx-projects: Circuit Playground Bluefruit (Josh + 4-year-old)

## Goal
Kid-friendly electronics projects in CircuitPython. Sessions of 15-20 minutes
with instant feedback (lights, sound, touch, screen). The kid makes the design
choices (colors, sounds, names); Josh types the code.

## Board and environment
- Board: Circuit Playground **Bluefruit** (nRF52840). It is NOT an Express.
- Bootloader was updated from 0.2.11 (too old for CircuitPython 8.2+) to 0.6.1+.
- CircuitPython 10.3.1 is installed. The board mounts as CIRCUITPY on D:
  (Git Bash: /d, WSL: /mnt/d).
- Libraries in lib/ (installed with circup): adafruit_circuitplayground,
  adafruit_lis3dh, adafruit_thermistor, neopixel, adafruit_pixelbuf,
  adafruit_bus_device.
- Import with: `from adafruit_circuitplayground import cp`
  (do not use the express module).
- Python 3.13 on Windows. Use Git Bash.

## Gotchas
- `python -m circup` does NOT work. Run `circup install <lib>` directly.
  If "command not found", add the Python Scripts folder to PATH, or use the
  full path to circup.exe.
- circup fails with "Missing file boot_out.txt" if the board hasn't rewritten
  it. Press reset once (single press) and retry.
- Double-tap reset enters the bootloader (green NeoPixels, BOOT drive).
  All-red NeoPixels usually means a USB/cable problem.
- Never delete files on CIRCUITPY (lib/, boot_out.txt, settings.toml).
  Only code.py (and project modules) get replaced.
- Flashing an Arduino sketch (needed for TensorFlow Lite) overwrites
  CircuitPython. Reinstall by dragging the CircuitPython .uf2 onto the BOOT drive.

## Repo layout
circuit-playground-projects/
  CLAUDE.md, README.md
  deploy.sh              # deploy.sh <NN|name|launcher>; also copies shared/*.py
  deploy.cmd             # same, from PowerShell: .\deploy 01
  shared/common.py       # pressed(), wants_exit(), exit_held(), beep()
  launcher/code.py       # menu; GAMES list of (module, color, tone)
  projects/NN-name/game_name.py + code.py + README.md
Each game lives once, in projects/NN-name/game_name.py, with a run() that
returns on A+B (common.wants_exit). code.py there just runs it standalone;
`deploy.sh launcher` copies every projects/*/game_*.py.
Launcher: button A = next game, B = start, A+B = exit. Import games lazily
and call gc.collect() (RAM is limited). Kid-editable settings go at the top
of game_*.py; game state goes inside run().
New game: add a project folder, then one line in GAMES.

## Shells
The Claude desktop Terminal panel opens PowerShell, which can't run .sh
files (it hands them to the file association). Josh uses `.\deploy`
there; Claude's Bash tool is Git Bash and uses ./deploy.sh. gh lives in
C:\Program Files\GitHub CLI (added to PATH in ~/.bashrc).

## Project ideas
Easy: shake-a-rainbow wand, hide-the-light nightlight, color mixer,
hot/cold meter, loudness meter.
Sound: fruit piano (capacitive touch on pads), light theremin, animal sounds.
Games: dice/counting, Simon Says, freeze dance, spinner, reaction race.
Useful: toothbrush timer, sunrise nightlight, treasure box lock.
Build: cardboard pet, flickering jack-o-lantern.
First evening: wand, fruit piano, dice.

## TFT Gizmo and animated buddy
- The kid designs an original hero character on paper (name, colors, mask).
  Scan or photograph it, shrink it to 240x240, and save it as a BMP.
- Animate by swapping face bitmaps: blink on a timer, eyes follow tilt,
  surprised on shake or loud noise, sleeps when the light sensor is covered.
- Button A cycles moods. NeoPixels glow in the hero's color.

## Later: TensorFlow Lite (Arduino, separate sketch)
- Magic-wand gesture recognition from the accelerometer.
- Keyword spotting from the microphone ("yes", "no", "go", "stop").
- Custom motion classifier trained on Josh's own data. Models must be tiny.

## Open items
- Verify the Gizmo's CircuitPython library works with the Bluefruit.
- Check pad/touch labels on the Bluefruit silkscreen.
- Check 3D-printed case fit: the Adafruit case STLs were made for the
  Express/Classic, not the Bluefruit.
- Bluetooth is available on this board but not used yet.
