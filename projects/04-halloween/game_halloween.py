# 04 Halloween: a spooky jukebox. Plays Halloween songs one after another
# with lights that match each song. A flickering jack-o'-lantern waits
# between songs.
#
# A:     next song
# B:     play / stop
# A+B:   back to the menu (in the launcher)
# Shake: lightning (and thunder when no song is playing)
# Touch any pad (no song playing): BOO!
# Cover the light sensor (no song playing): eyes in the dark
# Slide switch: sound on / off
#
# Your own songs go in halloween_songs.py (see halloween_songs_example.py).
import math
import random
import time
from adafruit_circuitplayground import cp
import common

# ---- Kid's choices ---------------------------------------------------------
ORANGE = (255, 80, 0)       # pumpkin
PURPLE = (120, 0, 200)      # witch
GREEN = (0, 255, 30)        # slime
GHOST = (60, 80, 120)       # ghost white-blue
WHITE = (255, 255, 255)     # lightning
CANDLE = (255, 140, 0)      # jack-o'-lantern flicker, with ORANGE
EYES = GREEN                # eyes in the dark
AUTOPLAY_NEXT = True        # after a song ends, play the next one
SHAKE_STRENGTH = 25         # higher = harder shake needed (resting is ~10)
DARK_FRACTION = 0.3         # "dark" = under 30% of the room's light at start
BRIGHTNESS = 0.2
# ----------------------------------------------------------------------------

# In the Hall of the Mountain King (Grieg, 1875, public domain). Speeds up
# every time it repeats. Also a working example of the note format.
MOUNTAIN_KING = """
B3:.5 C#4:.5 D4:.5 E4:.5 F#4:.5 D4:.5 F#4
F4:.5 C#4:.5 F4 E4:.5 C4:.5 E4
B3:.5 C#4:.5 D4:.5 E4:.5 F#4:.5 D4:.5 F#4:.5 B4:.5
A4:.5 F#4:.5 D4:.5 F#4:.5 A4:2
"""

BUILT_IN = [
    {"name": "Mountain King", "tempo": 100, "tempo_end": 260, "repeat": 4,
     "colors": (GREEN, PURPLE), "pattern": "chase", "notes": MOUNTAIN_KING},
]

try:
    from halloween_songs import SONGS as MY_SONGS
except ImportError:
    MY_SONGS = []

NOTE_STEPS = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def parse_note(token):
    """ "C#4:.5" -> (frequency, midi number, beats). Rests have frequency 0."""
    name, _, beats = token.partition(":")
    beats = float(beats) if beats else 1.0
    if name[0] in "Rr":
        return 0, 0, beats
    step = NOTE_STEPS[name[0].upper()]
    i = 1
    while name[i] in "#b":
        step += 1 if name[i] == "#" else -1
        i += 1
    midi = (int(name[i:]) + 1) * 12 + step
    return int(440 * 2 ** ((midi - 69) / 12)), midi, beats


class Player:
    """Plays a song in the background: call update() every frame."""

    def __init__(self, song):
        self.song = song
        self.notes = song["notes"].split()
        self.repeat = song.get("repeat", 1)
        self.total = max(1, len(self.notes) * self.repeat)
        self.i = 0
        self.loop = 0
        self.next_time = time.monotonic()
        self.off_time = 0

    def tempo(self):
        start = self.song["tempo"]
        end = self.song.get("tempo_end", start)
        done = (self.loop * len(self.notes) + self.i) / self.total
        return start + (end - start) * done

    def update(self, now):
        """Returns (freq, midi, beats) when a note starts, "done" at the
        end of the song, otherwise None."""
        if now >= self.off_time:
            cp.stop_tone()          # short gap so repeated notes sound apart
        if now < self.next_time:
            return None
        if now - self.next_time > 0.25:
            self.next_time = now    # we were held up (lightning, a button):
                                    # carry on instead of rushing to catch up
        if self.i >= len(self.notes):
            self.i = 0
            self.loop += 1
            if self.loop >= self.repeat:
                return "done"
        token = self.notes[self.i]
        length = 60 / self.tempo()
        self.i += 1
        try:
            freq, midi, beats = parse_note(token)
        except (KeyError, ValueError, IndexError):
            print("skipping bad note:", token)
            return None
        length *= beats
        cp.stop_tone()
        if freq and cp.switch:
            cp.start_tone(freq)
        self.next_time += length
        self.off_time = now + length * 0.9
        return freq, midi, beats


class Lights:
    """Our own copy of the 10 pixels, so patterns can fade them."""

    def __init__(self):
        self.buf = [(0, 0, 0)] * 10
        self.pos = 0

    def show(self):
        for p in range(10):
            cp.pixels[p] = self.buf[p]
        cp.pixels.show()

    def fade(self, amount, floor=(0, 0, 0)):
        for p in range(10):
            self.buf[p] = tuple(max(int(c * amount), f)
                                for c, f in zip(self.buf[p], floor))

    def fill(self, color):
        self.buf = [color] * 10

    def note(self, pattern, colors, freq, midi, beats):
        """Light up for a new note."""
        if not freq:
            return
        main, accent = colors
        long_note = beats >= 1
        if pattern == "pitch":
            # Higher notes light pixels further around the ring (G3 to G5).
            p = min(9, max(0, (midi - 55) * 10 // 24))
            self.buf[p] = main
            if long_note:
                self.buf[(p + 5) % 10] = accent
        elif pattern == "chase":
            self.pos = (self.pos + 1) % 10
            self.buf[self.pos] = main
            self.buf[self.pos - 1] = accent
        elif pattern == "pulse":
            self.fill(accent if long_note else main)
        elif pattern == "lightning":
            if long_note:
                self.fill(WHITE)
            else:
                self.buf[random.randint(0, 9)] = accent

    def frame(self, pattern, colors):
        """Fade a little every frame while a song plays."""
        if pattern == "lightning":
            self.fade(0.8, tuple(c // 6 for c in colors[0]))
        elif pattern == "pulse":
            self.fade(0.9)
        else:
            self.fade(0.85)

    def flicker(self):
        """Jack-o'-lantern candle."""
        for p in range(10):
            color = ORANGE if random.random() < 0.7 else CANDLE
            level = random.uniform(0.3, 1.0)
            self.buf[p] = tuple(int(c * level) for c in color)

    def eyes(self, now):
        self.fill((0, 0, 0))
        if now % 3 > 0.15:          # blink once every 3 seconds
            self.buf[2] = EYES
            self.buf[7] = EYES


def shaken():
    x, y, z = cp.acceleration
    return math.sqrt(x * x + y * y + z * z) > SHAKE_STRENGTH


def lightning(lights, thunder):
    for _ in range(2):
        cp.pixels.fill(WHITE)
        cp.pixels.show()
        time.sleep(0.05)
        cp.pixels.fill(0)
        cp.pixels.show()
        time.sleep(0.08)
    if thunder:
        for f in range(160, 50, -15):
            common.beep(f, 0.05)
    lights.fill((0, 0, 0))


def boo(lights):
    cp.pixels.fill(GHOST)
    cp.pixels.show()
    for f in range(700, 240, -30):
        common.beep(f, 0.03)
    lights.fill(GHOST)


def pad_touched():
    return (cp.touch_A1 or cp.touch_A2 or cp.touch_A3 or cp.touch_A4
            or cp.touch_A5 or cp.touch_A6 or cp.touch_TX)


def show_song_choice(songs, index):
    main, accent = songs[index]["colors"]
    cp.pixels.fill(0)
    for p in range(index + 1):      # one pixel per song number
        cp.pixels[p] = main if p % 2 == 0 else accent
    cp.pixels.show()
    print("song", index + 1, songs[index]["name"])
    common.beep(440 + index * 110, 0.12)
    time.sleep(0.6)


def run():
    cp.pixels.brightness = BRIGHTNESS
    cp.pixels.auto_write = False
    random.seed(int(time.monotonic() * 1000))
    # Measure the room now, so "covered" works in a bright or a dim room.
    dark_level = max(1, int(cp.light * DARK_FRACTION))

    songs = [s for s in MY_SONGS if s.get("notes", "").strip()] + BUILT_IN
    choice = 0
    player = None
    lights = Lights()
    last_flicker = 0
    last_touch = 0
    last_shake = 0
    show_song_choice(songs, choice)

    while True:
        now = time.monotonic()
        button = common.pressed()
        if common.wants_exit(button):
            cp.stop_tone()
            return
        if button == "A":
            cp.stop_tone()
            player = None
            choice = (choice + 1) % len(songs)
            show_song_choice(songs, choice)
        elif button == "B":
            cp.stop_tone()
            player = None if player else Player(songs[choice])
            lights.fill((0, 0, 0))

        if now - last_shake > 1 and shaken():
            last_shake = now
            lightning(lights, thunder=player is None)

        if player:
            song = songs[choice]
            event = player.update(time.monotonic())
            if event == "done":
                cp.stop_tone()
                player = None
                if AUTOPLAY_NEXT:
                    time.sleep(1)
                    choice = (choice + 1) % len(songs)
                    show_song_choice(songs, choice)
                    player = Player(songs[choice])
            elif event:
                lights.note(song["pattern"], song["colors"], *event)
            lights.frame(song["pattern"], song["colors"])
        else:
            if now - last_touch > 0.1:
                last_touch = now
                if pad_touched():
                    boo(lights)
            if cp.light < dark_level:
                lights.eyes(now)
            elif now - last_flicker > 0.08:
                last_flicker = now
                lights.flicker()

        lights.show()
        time.sleep(0.01)
