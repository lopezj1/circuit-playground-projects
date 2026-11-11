# 05 Buddy

An animated friend on the TFT Gizmo screen: your hero's picture, with eyes
that blink, look around when you tilt it, get surprised, and fall asleep in
the dark. Needs the
[TFT Gizmo](https://www.adafruit.com/product/4367) screwed on with all 12
screws.

| Do this | Buddy does |
|---|---|
| Wait | Blinks every few seconds |
| Tilt the board | Eyes roll toward the low side (needs pupils: the shape face, or `PICTURE_PUPILS = True`) |
| Shake, or make a loud noise | Surprised: big eyes, "Whoa!", a boing |
| Cover the light sensor (on the side with the lights) for 2 seconds | Falls asleep: eyes shut, "Z z z", lights dim. Uncover it, or press A or B, to wake it |
| A | Next face: happy, silly (wink), sad, angry |
| B | Next color scheme (the picture's own colors, then the ones in `COLOR_SCHEMES`) |
| Touch pad A1 | Says hi with a little tune and sparkly lights |
| A+B together | Back to the menu (when started from the launcher) |
| Slide switch | Sound on / off |

The lights glow in the buddy's color. In the launcher, Buddy is game 5 (sky
blue).

## Setup

The screen needs four libraries (circup adds the ones they depend on):

```bash
circup install adafruit_gizmo adafruit_st7789 adafruit_display_text adafruit_imageload
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
- `USE_PICTURE`: `False` shows the shape face even when there's a picture
- `PICTURE_PUPILS`: pupils inside the picture's eyes, or none
- `HERO_COLOR`: the shape face's color, as a hex color like `0x00A0FF`
- `LIGHT_COLOR`: the lights' color; `None` matches the face
- `COLOR_SCHEMES`: the color schemes B goes through. Each one recolors parts
  of the picture (`face`, `frame`, `line`, `ring`, `lens`) and the `lights`
- `SHAPE_COLORS`: the colors B goes through on the shape face
- `BACKGROUND`, `PUPIL_COLOR`, `MOUTH_COLOR`, `TONGUE_COLOR`
- `MOODS`: which moods A goes through, and in what order
- `HI_SONG`: the hello tune, as (frequency, seconds) pairs
- `BLINK_EVERY`: seconds between blinks, about
- `SHAKE_STRENGTH`, `LOUD_LEVEL`: how hard a shake or how loud a noise
  surprises it
- `SLEEP_IN_DARK`: `False` and it never falls asleep
- `DARK_FRACTION`, `DARK_SECONDS`: how dark, and for how long, before it
  falls asleep (0.2 = under 20% of the room's light)
- `LOOK_FLIP_X`, `LOOK_FLIP_Y`: set to `True` if the eyes look the wrong way

## Your hero's picture

Without a picture the buddy is a face made of shapes. To use a picture:

1. Draw the hero, or find a picture of it. Make the eyes plain white shapes,
   so the pupils and eyelids can move inside them.
2. Save it in this folder as `hero_source.png`, and turn it into the face
   (uv installs Pillow for you):

   ```bash
   uv run tools/make_face.py projects/05-buddy/hero_source.png
   ```

   This writes `hero.bmp` (240x240) and `hero_face.py` (where the eyes
   are, and which of the picture's colors is the face, the frame around the
   eyes, the line, the lenses or the border, for the color schemes).
   Check `hero_preview.png`: green outlines should hug both eyes.
3. Deploy. `deploy.sh` copies `hero.bmp` and `hero_face.py` to the board.

git ignores all the `hero*` files, so a picture of a character you don't own
never gets published. The eyelids use the color just around the eyes, and
the lights match it. Moods move the eyelids: a happy squint, a wink, sad or
angry slants.

## 20-minute plan
1. Meet the buddy: tilt it, shake it, clap, cover the lights to put it to bed.
2. Press A through the moods. Can your kid make the same faces?
3. Press B through the color schemes and pick a favorite. Touch A1 to hear
   it say hi.
4. Draw a new hero, or new eyes, and turn it into the face.
