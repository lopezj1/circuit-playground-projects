# 02 Fruit Piano

Each touch pad is a piano key with its own color. Clip a fruit to a pad with an
alligator clip and the fruit becomes the key.

| Pad | Note | Color |
|---|---|---|
| A1 | C | red |
| A2 | D | orange |
| A3 | E | yellow |
| A4 | F | green |
| A5 | G | light blue |
| A6 | A | blue |
| TX | B | purple |

A0 is the speaker pin, not a key. Check the silkscreen to confirm the labels.

| Do this | What happens |
|---|---|
| Touch a pad or fruit | Plays a note and lights up |
| A | Switches between low and high notes |
| B | Plays Twinkle Twinkle so they can copy it |
| A+B together | Back to the menu (when started from the launcher) |
| Slide switch | Sound on / off |

In the launcher, the fruit piano is game 2 (green).

## Kid's choices (top of `game_piano.py`)
- The colors in `KEYS`: "What color should the banana be?"
- `SONG`: write your own song with pad numbers (0 = A1 ... 6 = TX)

## Tips
- Touch is calibrated when a pad is first used after power-up. Clip the fruit on
  **before** you press reset, and don't touch the pads while the game starts.
- If notes play by themselves, set `TOUCH_ADJUST = 100` (or higher).
- Bananas, apples, grapes, and pickles all work. So does a cup of water with a
  wire in it.

## Run it on its own

```bash
./deploy.sh 02
```

From PowerShell, use `.\deploy 02` instead.

## 20-minute plan
1. Deploy it. Play the bare pads with a finger.
2. Pick fruits and clip them on, then reset. Play the fruit!
3. Press B to hear Twinkle. Can they play the first notes back? (A1 A1 A5 A5 A6 A6 A5)
4. Let them pick a new color for each fruit.
