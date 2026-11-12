# 06 Pet

A little pixel pet on the TFT Gizmo screen, like a Tamagotchi. It gets
hungry, lonely and tired, and asks for help: a chirp, and a picture above
its head of what it needs. Care for it and it cheers. It never dies: at
worst it's sad, or a little sick, until someone looks after it. Its needs
are saved, so they're still there after it's switched off. Needs the
[TFT Gizmo](https://www.adafruit.com/product/4367) screwed on with all 12
screws.

| It needs | It shows | Do this |
|---|---|---|
| Food | Sad, an apple above its head | Touch pad **A1** to feed it (a real fruit clipped to A1 works too). It won't eat when full |
| Love | Sad, a heart above its head | Touch pad **A2** to pet it |
| Sleep | Dozing, Zs | Cover the light sensor (the side with the lights) for 3 seconds. It only goes to bed when it's a bit tired, sleeps under a night sky, and wakes when it's light again or when it's rested |
| Cleaning | Poop next to it, a minute after eating | **Shake** the board (shaking only does something when there's poop) |
| A hug | Sick: green and sweaty, a heart above its head (a need was empty, or the poop was left, for a few minutes) | Pet it (A2), or let it sleep |

| Button | Does |
|---|---|
| A | "How are you?" The lights show its needs for 4 seconds: 3 orange for food, 3 pink for love, 3 blue for sleep, and one for health (green, brown with poop, yellow-green when sick) |
| B | Dress up: next suit color |
| A or B while it sleeps | Wakes it up |
| A+B together | Back to the menu (when started from the launcher) |
| Slide switch | Sound on / off |

When it has everything it needs, it walks around, blinks and sometimes
hops for joy. The lights glow in the color of its mood. In the launcher,
Pet is game 6 (gold).

## Setup

Same libraries as the buddy:

```bash
circup install adafruit_gizmo adafruit_st7789 adafruit_display_text adafruit_imageload
```

The pet needs `pet_sprites.bmp` in this folder. git ignores it, because the
current pet is drawn from a character we don't own; without it the screen
says "No pet_sprites.bmp". Make it with:

```bash
uv run tools/pet_frames.py
```

`tools/pet_frames.py` is private too. To make an original pet instead, draw
one on graph paper, 24x24 squares per frame, and save a BMP with the same
frames in the same order as `FRAMES` in `game_pet.py`: one row of 24x24
cells, 16 colors or fewer, palette color 0 = see-through, color 2 = the suit
(B changes it). An original pet can be committed.

## Run it on its own

```bash
./deploy.sh 06 --clean
```

`./deploy.sh launcher` puts the menu and every game back. From PowerShell,
use `.\deploy 06 --clean` instead.

## Saving

The needs, the poop, sick and the suit color are saved in the board's
non-volatile memory (`microcontroller.nvm`, which code can write even while
USB is connected) every 2 minutes and when you leave the game. The board
has no clock while it's off, so time stops: it just wakes up a little
hungrier. To start over, run this in the REPL:

```python
import microcontroller; microcontroller.nvm[0:4] = b"XXXX"
```

## Frames

Each mood is two frames swapped about twice a second, like a real Tamagotchi.

| Mood | Frames |
|---|---|
| idle | breathing, with a blink every few seconds |
| walk | one foot, then the other, walking across the screen |
| eat | chomping, while the apple gets eaten down to the core |
| happy | arms up and hop, with a floating heart |
| sad | head down, then a tear |
| sick | green, with a sweat drop |
| sleep | sitting slumped, breathing, Zs |

Props: apple, bitten apple, apple core, heart, Z, poop.

## Kid's choices (top of `game_pet.py`)
- `NAME`: the pet's name
- `SUIT_COLORS`: the suit colors B goes through
- `SKY`, `NIGHT`, `GRASS`: the background, at night, and the floor
- `NEED_COLORS`: the lights for food, love and sleep when you press A
- `FEED_SONG`, `PET_SONG`, `CLEAN_SONG`, `ASK_SONG`, `NO_SONG`: tunes as
  (frequency, seconds) pairs; frequency 0 is a rest

## How it behaves (grown-ups, also at the top of `game_pet.py`)
- `HUNGRY_AFTER`, `LONELY_AFTER`, `TIRED_AFTER`: minutes from full to empty
  (10, 8 and 20). Needs drop half as fast while it sleeps
- `SLEEP_REFILL`: minutes of sleep from empty to full
- `FEED`, `PET`: how much one snack or pat fills (100 = full)
- `LOW`: it asks for help at or below this
- `SICK_AFTER`, `POOP_AFTER`, `POOP_SICK_AFTER`: when it gets sick, and when
  the poop comes
- `WAKE_HUNGRY`: how much hungrier it is after being switched off
- `ASK_EVERY`: seconds between chirps while it needs something
- `TIME_SPEED`: 10 makes everything happen 10x faster, for testing
- `SAVE_MINUTES`: how often it saves
- `SHAKE_STRENGTH`, `DARK_FRACTION`, `DARK_SECONDS`: how hard a shake, and
  how dark for how long before it sleeps
- `BEDTIME`: it only goes to bed in the dark when sleep is under this (70),
  so a rested pet stays up even when the sensor is covered (lying screen-up
  on a table covers it)
- `FRAME_SECONDS`, `BLINK_EVERY`, `WALK_SPEED`: animation speeds
- `SHOW_NEEDS_TEXT`: the needs as numbers in the corner
- `BRIGHTNESS`

## 20-minute plan
1. Meet the pet. Press A: which lights are full?
2. Wait until it asks for something. What does the picture say it wants?
   Feed it, pet it, or put it to bed.
3. Feed it, wait a minute, and clean up with a shake.
4. Pick its suit color with B. Switch it off and on: is it still there?
