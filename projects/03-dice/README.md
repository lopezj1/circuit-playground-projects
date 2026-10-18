# 03 Dice

Shake (or press A) to roll. The lights spin, slow down, and then count up the
number one pixel at a time, with a beep for each one so you can count out loud.

| Do this | What happens |
|---|---|
| Shake or A | Roll |
| B | Switch between a 6-sided and a 10-sided die (dim pixels show which) |
| A+B together | Back to the menu (when started from the launcher) |
| Slide switch | Sound on / off |

In the launcher, the dice are game 3 (orange).

## Kid's choices (top of `game_dice.py`)
- `NUMBER_COLORS`: a color for each number
- `SPIN_COLOR`: the color of the spinning light

## Game ideas
- **Count along**: say each number out loud as it beeps.
- **Hop game**: roll, then hop that many times.
- **Who's bigger**: take turns rolling. The bigger number wins.
- Switch to 10 sides with B once counting to 6 is easy.

## Run it on its own

```bash
./deploy.sh 03
```

From PowerShell, use `.\deploy 03` instead.
