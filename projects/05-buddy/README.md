# 05 Buddy

An animated friend on the TFT Gizmo screen. It blinks, looks around when you
tilt it, gets surprised, and falls asleep in the dark. Needs the
[TFT Gizmo](https://www.adafruit.com/product/4367) screwed on with all 12
screws.

| Do this | Buddy does |
|---|---|
| Wait | Blinks every few seconds |
| Tilt the board | Eyes roll toward the low side |
| Shake, or make a loud noise | Surprised: big eyes, "Whoa!", a boing |
| Cover the light sensor (on the side with the lights) | Falls asleep: eyes shut, "Z z z", lights dim. Uncover to wake it |
| A | Next mood: happy, silly, sad, angry |
| B | Says hi with a little tune and sparkly lights |
| A+B together | Back to the menu (when started from the launcher) |
| Slide switch | Sound on / off |

The lights glow in the buddy's color. In the launcher, Buddy is game 5 (sky
blue).

## Setup

The screen needs three libraries (circup adds the ones they depend on):

```bash
circup install adafruit_gizmo adafruit_st7789 adafruit_display_text
```

## Run it on its own

```bash
./deploy.sh 05 --clean
```

`--clean` removes the other games' files from the board, so only the buddy
is there. `./deploy.sh launcher` puts the menu and every game back. From
PowerShell, use `.\deploy 05 --clean` instead.

## Kid's choices (top of `game_buddy.py`)
- `NAME`: the buddy says "Hi, I'm NAME!"
- `HERO_COLOR`: face and lights, as a hex color like `0x00A0FF`
- `BACKGROUND`, `PUPIL_COLOR`, `MOUTH_COLOR`, `TONGUE_COLOR`
- `MOODS`: which moods A goes through, and in what order
- `HI_SONG`: the hello tune, as (frequency, seconds) pairs
- `BLINK_EVERY`: seconds between blinks, about
- `SHAKE_STRENGTH`, `LOUD_LEVEL`: how hard a shake or how loud a noise
  surprises it
- `DARK_FRACTION`: how dark it has to be to fall asleep
- `LOOK_FLIP_X`, `LOOK_FLIP_Y`: set to `True` if the eyes look the wrong way

## Coming next: the kid's own hero

The face is drawn with shapes for now. Next, your kid draws a hero on paper
(name, colors, mask). A photo of the drawing gets shrunk to a 240x240 BMP
and becomes the face, with the moving pupils, blinking lids and mouth drawn
on top. Draw the eyes as empty white circles so the pupils can move.

## 20-minute plan
1. Meet the buddy: tilt it, shake it, clap, cover the lights to put it to bed.
2. Press A through the moods. Can your kid make the same faces?
3. Pick the buddy's name and color, then press B to hear it say hi.
4. Start drawing the hero that will replace the shape face.
