# 06 Pet

A little pixel pet on the TFT Gizmo screen, like a Tamagotchi. It breathes,
blinks, walks back and forth, eats, cheers, cries, gets sick and sleeps.
Needs the [TFT Gizmo](https://www.adafruit.com/product/4367) screwed on
with all 12 screws.

This is Phase 0 of the plan in
[issue #2](https://github.com/lopezj1/circuit-playground-projects/issues/2):
the pet and its animations. Needs that run down, saving and growing up come
next.

| Do this | Pet does |
|---|---|
| A | Next mood: idle, walk, eat, happy, sad, sick, sleep |
| B | Previous mood |
| Touch pad A1 | Eats an apple ("nom nom"), then cheers |
| Touch pad A2 | Gets petted: cheers with a heart |
| A+B together | Back to the menu (when started from the launcher) |
| Slide switch | Sound on / off |

The lights match the mood. In the launcher, Pet is game 6 (gold).

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
cells, 16 colors or fewer, palette color 0 = see-through. An original pet can
be committed.

## Run it on its own

```bash
./deploy.sh 06 --clean
```

`./deploy.sh launcher` puts the menu and every game back. From PowerShell,
use `.\deploy 06 --clean` instead.

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
| sleep | sitting slumped, breathing, Zs, night sky |

Props: apple, bitten apple, apple core, heart, Z, poop.

## Kid's choices (top of `game_pet.py`)
- `NAME`: the pet's name
- `MOODS`: which moods A and B go through, and in what order
- `SKY`, `NIGHT`, `GRASS`: the background, at night, and the floor
- `LIGHT_COLORS`: the lights' color for each mood
- `FRAME_SECONDS`: how fast it animates
- `BLINK_EVERY`: seconds between blinks, about
- `WALK_SPEED`: how fast it walks
- `FEED_SONG`, `PET_SONG`: tunes as (frequency, seconds) pairs
- `SHOW_MOOD_NAME`: the mood's name in the corner, for grown-ups
- `BRIGHTNESS`

## 20-minute plan
1. Press A through the moods. Can your kid act out each one?
2. Feed it (A1) and pet it (A2).
3. Pick the sky, grass and light colors.
4. On graph paper, draw what your own pet would look like.
