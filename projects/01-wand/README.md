# 01 Wand

Shake the board to cast a spell. It glows softly while it waits.

| Do this | What happens |
|---|---|
| Shake | Casts the current spell, then it fades out |
| A | Next spell (the number of lit pixels shows which one) |
| B | Lights out (shake to wake it up) |
| A+B together | Back to the menu (when started from the launcher) |
| Slide switch | Sound on / off |

Spells: **rainbow** (spinning rainbow with a rising whoosh), **sparkle** (twinkles),
**favorite** (fills up in the favorite color).

In the launcher, the wand is game 1 (purple).

## Kid's choices (top of `game_wand.py`)
- `FAVORITE`: the resting glow color. Ask: "What color is your wand?"
- `RAINBOW`: reorder it or swap in new colors
- `SHAKE_STRENGTH`: make it easier (15) or harder (30) to trigger

## Run it on its own

```bash
./deploy.sh 01
```

From PowerShell, use `.\deploy 01` instead.

## 15-minute plan
1. Deploy it, then hand over the wand and let them discover shake.
2. Show them A. Which spell is their favorite?
3. Change `FAVORITE` to their color and redeploy. It's their wand now.
4. Bonus: tape it to a paper-towel tube or a stick.
