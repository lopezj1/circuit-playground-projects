# 05 Buddy: an animated friend on the TFT Gizmo screen.
#
# Wait:            blinks now and then
# Tilt:            eyes look around
# Shake, or a loud noise: surprised!
# Cover the light sensor (the side with the lights): falls asleep
# A:               next mood (happy, silly, sad, angry)
# B:               says hi
# A+B:             back to the menu (in the launcher)
# Slide switch:    sound on / off
#
# The face is drawn with shapes for now. Later the kid's own drawing can
# replace it.
import math
import random
import time
import displayio
import terminalio
import vectorio
from adafruit_display_text import label
from adafruit_gizmo import tft_gizmo
from adafruit_circuitplayground import cp
import common

# ---- Kid's choices ---------------------------------------------------------
NAME = "Buddy"
HERO_COLOR = 0x00A0FF       # face and lights
BACKGROUND = 0x000000       # around the face
PUPIL_COLOR = 0x000000
MOUTH_COLOR = 0x300010
TONGUE_COLOR = 0xFF4070
MOODS = ["happy", "silly", "sad", "angry"]
HI_SONG = [(523, 0.1), (659, 0.1), (784, 0.1), (1047, 0.2)]
BLINK_EVERY = 4             # seconds, about
SHAKE_STRENGTH = 25         # higher = harder shake needed (resting is ~10)
LOUD_LEVEL = 400            # higher = louder noise needed (quiet room ~20)
DARK_FRACTION = 0.3         # "dark" = under 30% of the brightest light seen
LOOK_FLIP_X = False         # eyes look the wrong way left/right? set True
LOOK_FLIP_Y = False         # eyes look the wrong way up/down? set True
BRIGHTNESS = 0.2            # lights
# ----------------------------------------------------------------------------

EYES = ((80, 95), (160, 95))
EYE_SIZE = 26
PUPIL_SIZE = 11
LOOK_RANGE = 12             # how far the pupils move
LID_HEIGHT = 58
MOUTH_Y = 165


def rgb(color):
    return ((color >> 16) & 255, (color >> 8) & 255, color & 255)


def paint(color):
    palette = displayio.Palette(1)
    palette[0] = color
    return palette


def smile(width, bend, thick, steps=10):
    """Mouth shape: bend > 0 smiles, bend < 0 frowns, 0 is flat."""
    top = []
    bottom = []
    for i in range(steps + 1):
        t = i * 2 / steps - 1
        x = int(t * width)
        y = int(bend * (1 - t * t))
        top.append((x, y))
        bottom.append((x, y + int(thick * (1 - 0.6 * t * t)) + 2))
    return top + bottom[::-1]


def brow(x, y, tilt):
    """Eyebrow from x-28 to x+28. tilt > 0 lifts the right end."""
    return [(x - 28, y + tilt), (x + 28, y - tilt),
            (x + 28, y - tilt + 7), (x - 28, y + tilt + 7)]


class Face:
    def __init__(self):
        self.root = displayio.Group()
        face_paint = paint(HERO_COLOR)
        self.root.append(vectorio.Rectangle(
            pixel_shader=paint(BACKGROUND), width=240, height=240, x=0, y=0))
        self.root.append(vectorio.Circle(
            pixel_shader=face_paint, radius=112, x=120, y=120))

        white = paint(0xFFFFFF)
        black = paint(PUPIL_COLOR)
        self.whites = []
        self.pupils = []
        self.lids = []
        for x, y in EYES:
            w = vectorio.Circle(pixel_shader=white, radius=EYE_SIZE, x=x, y=y)
            p = vectorio.Circle(pixel_shader=black, radius=PUPIL_SIZE, x=x, y=y)
            lid = vectorio.Polygon(pixel_shader=face_paint,
                                   points=[(0, 0), (1, 0), (1, 1)],
                                   x=x - 31, y=y - EYE_SIZE - 3)
            self.root.append(w)
            self.root.append(p)
            self.root.append(lid)
            self.whites.append(w)
            self.pupils.append(p)
            self.lids.append(lid)

        mouth_paint = paint(MOUTH_COLOR)
        self.brows = displayio.Group()
        self.brow_shapes = [
            vectorio.Polygon(pixel_shader=mouth_paint, points=brow(0, 0, 0),
                             x=0, y=0) for _ in EYES]
        for b in self.brow_shapes:
            self.brows.append(b)
        self.root.append(self.brows)

        self.mouth = displayio.Group()
        self.mouth_shape = vectorio.Polygon(
            pixel_shader=mouth_paint, points=smile(40, 20, 12), x=120, y=MOUTH_Y)
        self.mouth.append(self.mouth_shape)
        self.root.append(self.mouth)

        self.tongue = displayio.Group()
        self.tongue.append(vectorio.Circle(
            pixel_shader=paint(TONGUE_COLOR), radius=11, x=134, y=MOUTH_Y + 26))
        self.root.append(self.tongue)

        self.oh = displayio.Group()     # surprised "O" mouth
        self.oh.append(vectorio.Circle(
            pixel_shader=mouth_paint, radius=18, x=120, y=MOUTH_Y + 12))
        self.root.append(self.oh)

        self.zzz = label.Label(terminalio.FONT, text="Z z z", color=0xFFFFFF,
                               scale=3, x=140, y=28)
        self.root.append(self.zzz)
        self.words = label.Label(terminalio.FONT, text=" ", color=0x000000,
                                 background_color=0xFFFFFF, scale=2,
                                 anchor_point=(0.5, 1.0),
                                 anchored_position=(120, 236))
        self.root.append(self.words)
        self.lid_now = None
        self.look(0, 0)
        self.lids_closed(0)
        self.say("")

    def look(self, dx, dy):
        for (x, y), p in zip(EYES, self.pupils):
            p.x = x + int(dx)
            p.y = y + int(dy)

    def eyes_wide(self, wide):
        for w, p in zip(self.whites, self.pupils):
            w.radius = EYE_SIZE + 6 if wide else EYE_SIZE
            p.radius = PUPIL_SIZE - 4 if wide else PUPIL_SIZE

    def lids_closed(self, amount):
        """0 = eyes open, 1 = shut."""
        h = max(2, int(LID_HEIGHT * amount))
        if h == self.lid_now:
            return
        self.lid_now = h
        for lid in self.lids:
            lid.points = [(0, 0), (62, 0), (62, h), (0, h)]

    def mood(self, name):
        self.oh.hidden = True
        self.mouth.hidden = False
        self.tongue.hidden = name != "silly"
        self.brows.hidden = name not in ("sad", "angry")
        mouth = {"happy": smile(42, 22, 14), "silly": smile(42, 22, 14),
                 "sad": smile(34, -16, 10), "angry": smile(32, -5, 9),
                 "sleep": smile(16, 0, 5)}[name]
        self.mouth_shape.points = mouth
        self.mouth_shape.y = MOUTH_Y + (12 if name in ("sad", "sleep") else 0)
        tilt = 7 if name == "sad" else -9
        for (x, y), b in zip(EYES, self.brow_shapes):
            inner = 1 if x < 120 else -1    # right end is "inner" on the left eye
            b.points = brow(x, y - EYE_SIZE - 14, tilt * inner)

    def surprised(self):
        self.mouth.hidden = True
        self.tongue.hidden = True
        self.brows.hidden = True
        self.oh.hidden = False

    def say(self, text):
        self.words.text = text if text else " "
        self.words.hidden = not text


def boing():
    for f in range(300, 1000, 70):
        common.beep(f, 0.02)


def say_hi(face, display):
    face.say("Hi, I'm " + NAME + "!")
    face.mood("happy")
    face.look(0, 0)
    display.refresh()
    hero = rgb(HERO_COLOR)
    for i, (freq, seconds) in enumerate(HI_SONG):
        cp.pixels.fill(0)
        for p in range(i, 10, len(HI_SONG)):
            cp.pixels[p] = hero
        cp.pixels[(i * 3 + 1) % 10] = (255, 255, 255)
        cp.pixels.show()
        common.beep(freq, seconds)
    time.sleep(0.8)


def run():
    hero = rgb(HERO_COLOR)
    cp.pixels.brightness = BRIGHTNESS
    cp.pixels.auto_write = False
    random.seed(int(time.monotonic() * 1000))

    displayio.release_displays()
    display = tft_gizmo.TFT_Gizmo()
    display.auto_refresh = False
    face = Face()
    display.root_group = face.root

    try:
        play(face, display, hero)
    finally:
        display.brightness = 0
        display.root_group = None
        displayio.release_displays()


def play(face, display, hero):
    mood = 0
    state = "awake"             # awake, surprised, asleep
    state_until = 0
    face.mood(MOODS[mood])
    look_x = look_y = 0.0
    next_blink = time.monotonic() + BLINK_EVERY
    next_sense = 0
    light = brightest = max(1, cp.light)
    dark_since = None

    while True:
        now = time.monotonic()
        button = common.pressed()
        if common.wants_exit(button):
            cp.stop_tone()
            return
        if button == "A" and state != "asleep":
            mood = (mood + 1) % len(MOODS)
            face.mood(MOODS[mood])
            common.beep(440 + mood * 110, 0.08)
        elif button == "B" and state != "asleep":
            say_hi(face, display)
            face.say("")
            face.mood(MOODS[mood])
            state = "awake"

        # Sensors, ten times a second.
        startle = False
        if now >= next_sense:
            next_sense = now + 0.1
            x, y, z = cp.acceleration
            if math.sqrt(x * x + y * y + z * z) > SHAKE_STRENGTH:
                startle = True
            elif state != "surprised" and cp.sound_level > LOUD_LEVEL:
                startle = True
            light = light * 0.7 + cp.light * 0.3
            brightest = max(brightest * 0.9995, light, 1)
            if light < brightest * DARK_FRACTION:
                dark_since = dark_since or now
            else:
                dark_since = None
            # Googly eyes: they roll toward the low side.
            tx = max(-1, min(1, x / 7)) * (-1 if LOOK_FLIP_X else 1)
            ty = max(-1, min(1, z / 7)) * (-1 if LOOK_FLIP_Y else 1)
            look_x += (tx * LOOK_RANGE - look_x) * 0.5
            look_y += (ty * LOOK_RANGE - look_y) * 0.5

        if startle and state != "surprised":
            state = "surprised"
            state_until = now + 1.5
            face.lids_closed(0)
            face.eyes_wide(True)
            face.surprised()
            face.say("Whoa!")
            cp.pixels.fill((255, 255, 255))
            cp.pixels.show()
            display.refresh()
            boing()
        elif state == "surprised" and now > state_until:
            state = "awake"
            face.eyes_wide(False)
            face.mood(MOODS[mood])
            face.say("")
        elif state == "awake" and dark_since and now - dark_since > 0.5:
            state = "asleep"
            face.mood("sleep")
            face.lids_closed(1)
            common.beep(330, 0.15)
            common.beep(262, 0.3)
        elif state == "asleep" and not dark_since:
            state = "awake"
            face.mood(MOODS[mood])
            face.lids_closed(0)
            common.beep(523, 0.08)
            common.beep(784, 0.12)
            next_blink = now + BLINK_EVERY

        if state == "asleep":
            face.zzz.hidden = False
            face.zzz.y = 28 + int(4 * math.sin(now * 2))
            level = 0.04 + 0.03 * math.sin(now * 1.5)
            cp.pixels.fill(tuple(int(c * level) for c in hero))
        else:
            face.zzz.hidden = True
            face.look(look_x, look_y)
            if state == "awake":
                if now >= next_blink:
                    face.lids_closed(1)
                    if now >= next_blink + 0.15:
                        face.lids_closed(0)
                        next_blink = now + BLINK_EVERY * random.uniform(0.5, 1.5)
                glow = 0.6 + 0.4 * math.sin(now * 2)
                cp.pixels.fill(tuple(int(c * glow) for c in hero))
        cp.pixels.show()
        display.refresh()
        time.sleep(0.02)
