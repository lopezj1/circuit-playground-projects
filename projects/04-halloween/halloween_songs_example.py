# Template for your own Halloween songs.
#
# Copy this file to halloween_songs.py in the same folder and type the
# melodies in there. git ignores halloween_songs.py, so songs you type in
# (including copyrighted ones) stay on your computer and the board and are
# never published. deploy.sh copies it to the board for you.
#
# How to write notes: NAME + OCTAVE : BEATS, separated by spaces or new lines.
#   C4 is middle C. Sharps: C#4. Flats: Eb4. A rest (silence): R
#   Beats: 1 = one beat, .5 = half a beat, 2 = two beats. A note with no
#   ":beats" lasts one beat.
#   Example, a scale with a rest and a long note at the end:
#     "C4:.5 D4:.5 E4:.5 F4:.5 G4 R:.5 C5:2"
#   See MOUNTAIN_KING in game_halloween.py for a whole song.
#
# Each song picks:
#   tempo      beats per minute. Optional "tempo_end" speeds up (or slows
#              down) to that tempo by the end.
#   repeat     optional, how many times to play it through
#   colors     (main, accent)
#   pattern    "pitch"     notes light the ring by how high they are
#              "chase"     a dot runs around the ring, one step per note
#              "pulse"     the whole ring flashes on every note
#              "lightning" dark ring with white flashes on long notes
#
# Songs with empty notes are skipped, so it's fine to fill them in one at a
# time.

ORANGE = (255, 80, 0)
PURPLE = (120, 0, 200)
GREEN = (0, 255, 30)
RED = (200, 0, 0)

SONGS = [
    {
        "name": "This Is Halloween",
        "tempo": 140,
        "colors": (ORANGE, PURPLE),
        "pattern": "pitch",
        "notes": """
        """,
    },
    {
        "name": "Halloween theme",
        "tempo": 120,
        "colors": (ORANGE, RED),
        "pattern": "pulse",
        "notes": """
        """,
    },
    {
        "name": "Thriller",
        "tempo": 118,
        "colors": (PURPLE, GREEN),
        "pattern": "chase",
        "notes": """
        """,
    },
]
