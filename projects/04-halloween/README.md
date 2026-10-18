# 04 Halloween

A spooky jukebox. It plays Halloween songs one after another, with lights that
match each song. Between songs, a jack-o'-lantern flickers.

| Do this | What happens |
|---|---|
| A | Next song (pixels show the song number in its colors) |
| B | Play / stop |
| A+B together | Back to the menu (when started from the launcher) |
| Shake | Lightning! (plus thunder when no song is playing) |
| Touch any pad | BOO! with a ghost flash (no song playing) |
| Cover the light sensor (next to the eye symbol on the board) | Green eyes blink in the dark (no song playing) |
| Slide switch | Sound on / off |

In the launcher, Halloween is game 4 (pumpkin orange).

## Songs

| Song | Colors | Lights |
|---|---|---|
| This Is Halloween | orange + purple | **pitch**: higher notes light pixels further around the ring |
| Halloween theme | orange + red | **pulse**: the whole ring flashes on every note |
| Thriller | purple + green | **chase**: a dot runs around the ring, one step per note |
| Mountain King (built in) | green + purple | **chase**, speeding up each time it repeats |

### Adding your songs

The first three songs are copyrighted, so their notes aren't in this public
repo. You type them into a private file:

1. Copy `halloween_songs_example.py` to `halloween_songs.py` in this folder.
2. Type each melody into its `"notes"` using note names, like
   `"E4:.5 G4:.5 A4 R:.5 B4:2"`. The template explains the format.
3. Deploy. `deploy.sh` copies `halloween_songs.py` to the board.

git ignores `halloween_songs.py`, so it never gets pushed. Songs with no notes
are skipped, so you can fill them in one at a time. Until then, the built-in
Mountain King plays (Grieg, 1875, public domain).

If a note is mistyped, the game skips it and prints `skipping bad note` to
the serial console.

## Kid's choices (top of `game_halloween.py`)
- Colors: `ORANGE`, `PURPLE`, `GREEN`, `GHOST`, `CANDLE`, `EYES`
- `AUTOPLAY_NEXT`: keep playing the next song, or stop after one
- `SHAKE_STRENGTH`: how hard a shake makes lightning
- `DARK_FRACTION`: how dark it has to be for the eyes to appear, compared
  with the room's light when the game starts (0.3 = 30%). Don't cover the
  board while the game starts.
- Each song's colors and light pattern are in `halloween_songs.py`

## Run it on its own

```bash
./deploy.sh 04
```

From PowerShell, use `.\deploy 04` instead.

## 20-minute plan
1. Play the jack-o'-lantern: shake for lightning, touch for BOO, cover the
   light sensor for eyes.
2. Press B and dance to the songs. Which lights go with which song?
3. Let them pick new colors or swap the light patterns between songs.
4. Lights off: put it inside a paper or plastic pumpkin.
