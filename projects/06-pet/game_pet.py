# 06 Pet: a little pixel pet on the TFT Gizmo, like a Tamagotchi.
#
# Phase 0 of the plan (GitHub issue #2): the pet and its animations.
# A and B go through the moods, touch A1 to feed it, touch A2 to pet it.
# Needs that run down, saving and growing up come next.
import random
import time

import board
import busio
import displayio
import terminalio
import vectorio
from adafruit_display_text import label
from adafruit_gizmo import tft_gizmo
from adafruit_circuitplayground import cp
import common

# ---- Kid's choices ---------------------------------------------------------
NAME = "Spin"
MOODS = ["idle", "walk", "eat", "happy", "sad", "sick", "sleep"]  # A/B order
SKY = 0x87CEEB              # background
NIGHT = 0x14143C            # background while it sleeps
GRASS = 0x3FAE3F            # the floor
LIGHT_COLORS = {"idle": 0xCB0002, "walk": 0xCB0002, "eat": 0xFF8000,
                "happy": 0xFF6FA5, "sad": 0x2040FF, "sick": 0x40C000,
                "sleep": 0x100020}
FRAME_SECONDS = 0.5         # how long each animation frame shows
BLINK_EVERY = 4             # seconds between blinks, about
WALK_SPEED = 2              # steps per frame while walking
FEED_SONG = [(523, 0.08), (659, 0.08), (523, 0.08), (659, 0.08)]  # nom nom
PET_SONG = [(392, 0.12), (523, 0.12), (784, 0.2)]
SHOW_MOOD_NAME = True       # small mood name in the corner (for grown-ups)
BRIGHTNESS = 0.2
# ----------------------------------------------------------------------------

PICTURE = "pet_sprites.bmp"
CELL = 24                   # each frame is 24x24 pixels in the picture
SCALE = 6                   # the pet is drawn 6x: 144x144 on the screen
PROP_SCALE = 4              # food, hearts and Zs are drawn 4x
FLOOR_Y = 216
PET_Y = FLOOR_Y - CELL * SCALE
MIDDLE = (240 - CELL * SCALE) // 2
# The frames in the picture, left to right (tools/pet_frames.py makes them).
FRAMES = ["idle0", "idle1", "blink", "walk0", "walk1", "eat0", "eat1",
          "happy0", "happy1", "sad0", "sad1", "sick0", "sick1",
          "sleep0", "sleep1", "apple", "apple_bite", "apple_core", "heart",
          "z", "poop"]
ANIMATIONS = {mood: (mood + "0", mood + "1") for mood in MOODS}


def paint(color):
    p = displayio.Palette(1)
    p[0] = color
    return p


class Pet:
    """The pet, its food/heart/Z prop, the sky and the grass."""

    def __init__(self):
        import adafruit_imageload
        sheet, palette = adafruit_imageload.load(
            PICTURE, bitmap=displayio.Bitmap, palette=displayio.Palette)
        palette.make_transparent(0)
        self.root = displayio.Group()
        self.sky = paint(SKY)
        self.root.append(vectorio.Rectangle(pixel_shader=self.sky, width=240,
                                            height=FLOOR_Y, x=0, y=0))
        self.root.append(vectorio.Rectangle(pixel_shader=paint(GRASS), width=240,
                                            height=240 - FLOOR_Y, x=0, y=FLOOR_Y))

        def sprite(scale):
            grid = displayio.TileGrid(sheet, pixel_shader=palette,
                                      tile_width=CELL, tile_height=CELL)
            group = displayio.Group(scale=scale)
            group.append(grid)
            self.root.append(group)
            return group, grid

        self.body_group, self.body = sprite(SCALE)
        self.prop_group, self.prop = sprite(PROP_SCALE)
        self.body_group.x, self.body_group.y = MIDDLE, PET_Y
        self.prop_group.hidden = True
        self.name = label.Label(terminalio.FONT, text="", color=0xFFFFFF, x=4, y=8)
        self.name.hidden = not SHOW_MOOD_NAME
        self.root.append(self.name)
        self.frame = self.prop_name = None

    def show(self, frame, x=None, y=PET_Y):
        if frame != self.frame:
            self.body[0] = FRAMES.index(frame)
            self.frame = frame
        if x is not None:
            self.body_group.x = x
        self.body_group.y = y

    def face(self, left):
        self.body.flip_x = left

    def show_prop(self, name, x=0, y=0):
        """name is a prop frame, or None to hide it. x, y: where the prop's
        middle goes on the screen."""
        if name is None:
            self.prop_group.hidden = True
            return
        if name != self.prop_name:
            self.prop[0] = FRAMES.index(name)
            self.prop_name = name
        half = CELL * PROP_SCALE // 2
        self.prop_group.x, self.prop_group.y = x - half, y - half
        self.prop_group.hidden = False

    def night(self, dark):
        self.sky[0] = NIGHT if dark else SKY


def song(notes):
    for freq, seconds in notes:
        common.beep(freq, seconds)


def run():
    cp.pixels.brightness = BRIGHTNESS
    cp.pixels.auto_write = False
    random.seed(int(time.monotonic() * 1000))

    # Our own SPI bus, so the next start (from the launcher) doesn't fail
    # with "A4 in use".
    displayio.release_displays()
    spi = busio.SPI(board.SCL, MOSI=board.SDA)
    display = tft_gizmo.TFT_Gizmo(spi=spi)
    try:
        display.auto_refresh = False
        try:
            pet = Pet()
        except OSError:
            missing(display)
            return
        display.root_group = pet.root
        play(pet, display)
    finally:
        cp.pixels.fill(0)
        cp.pixels.show()
        display.brightness = 0
        display.root_group = None
        displayio.release_displays()
        spi.deinit()


def missing(display):
    """No sprite picture on the board: say so until A+B (or forever)."""
    group = displayio.Group()
    group.append(label.Label(terminalio.FONT, color=0xFFFFFF, scale=2, x=10, y=90,
                             text="No " + PICTURE + "\nSee projects/06-pet\nREADME"))
    display.root_group = group
    display.refresh()
    cp.pixels.fill(0x400000)
    cp.pixels.show()
    while not common.wants_exit(common.pressed()):
        time.sleep(0.05)


def play(pet, display):
    choice = 0                  # the mood A and B picked
    mood = None
    care = []                   # [(mood, seconds)] from feeding or petting
    care_until = 0
    tick = 0                    # which frame of the animation (0 or 1)
    next_frame = 0
    next_blink = time.monotonic() + BLINK_EVERY
    x, left = MIDDLE, False
    prop_step = 0
    last_touch = 0

    while True:
        now = time.monotonic()
        button = common.pressed()
        if common.wants_exit(button):
            return
        if button in ("A", "B"):
            care = []
            care_until = 0
            choice = (choice + (1 if button == "A" else -1)) % len(MOODS)
            common.beep(660 if button == "A" else 440, 0.05)

        if now - last_touch > 1:
            if cp.touch_A1:
                care = [("eat", 4.5), ("happy", 2)]
                care_until = 0
                last_touch = now
            elif cp.touch_A2:
                care = [("happy", 3)]
                care_until = 0
                last_touch = now

        # Feeding and petting take over for a few seconds, then back to
        # whatever mood A and B picked.
        want = MOODS[choice]
        if care and care_until == 0:
            care_until = now + care[0][1]
            if care[0][0] == "eat":
                song(FEED_SONG)
            elif len(care) == 1:
                song(PET_SONG)
        if care and now >= care_until:
            care.pop(0)
            care_until = 0
            continue
        if care:
            want = care[0][0]

        if want != mood:
            mood = want
            tick, next_frame, prop_step = 0, 0, 0
            if mood != "walk":
                x, left = MIDDLE, False
                pet.face(left)
            pet.night(mood == "sleep")
            pet.name.text = mood
            cp.pixels.fill(LIGHT_COLORS[mood])
            cp.pixels.show()

        if now < next_frame:
            time.sleep(0.02)
            continue
        next_frame = now + FRAME_SECONDS
        tick = 1 - tick
        frame = ANIMATIONS[mood][tick]
        y = PET_Y

        if mood == "idle" and now >= next_blink:
            frame = "blink"
            next_frame = now + 0.2
            tick = 1                # back to idle0 next
            next_blink = now + BLINK_EVERY * random.uniform(0.6, 1.4)
        elif mood == "walk":
            x += (-1 if left else 1) * WALK_SPEED * SCALE
            if x <= 0 or x >= 240 - CELL * SCALE:
                x = max(0, min(240 - CELL * SCALE, x))
                left = not left
                pet.face(left)
        elif mood == "happy" and tick == 0:
            y = PET_Y - 2 * SCALE   # hop, arms up

        pet.show(frame, x, y)

        # Props: the apple gets eaten, hearts and Zs float up.
        prop_step += 1
        if mood == "eat":
            bites = ["apple", "apple", "apple_bite", "apple_bite", "apple_core",
                     "apple_core"]
            pet.show_prop(bites[min(prop_step - 1, len(bites) - 1)], x + 150, 162)
        elif mood == "happy":
            pet.show_prop("heart", x + 112, 50 - 8 * (prop_step % 4))
        elif mood == "sleep":
            pet.show_prop("z", x + 120, 90 - 12 * (prop_step % 5))
        else:
            pet.show_prop(None)

        display.refresh()
