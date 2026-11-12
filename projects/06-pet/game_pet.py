# 06 Pet: a little pixel pet on the TFT Gizmo, like a Tamagotchi.
#
# It gets hungry, lonely and tired, and asks for help with a chirp and a
# picture of what it needs. Touch A1 to feed it, touch A2 to pet it, cover
# the light sensor so it can sleep, shake to clean up after it. It never
# dies: at worst it's sad or a little sick until it's cared for. Its needs
# are saved, so they're still there after it's switched off.
# The plan is GitHub issue #2.
import math
import random
import struct
import time

import board
import busio
import displayio
import microcontroller
import terminalio
import vectorio
from adafruit_display_text import label
from adafruit_gizmo import tft_gizmo
from adafruit_circuitplayground import cp
import common

# ---- Kid's choices ---------------------------------------------------------
NAME = "Spin"
SUIT_COLORS = [0xCB0002, 0x1E50D0, 0x7A2BC0, 0x1A1A1A]  # B: red, blue, purple, black
SKY = 0x87CEEB              # background
NIGHT = 0x14143C            # background while it sleeps
GRASS = 0x3FAE3F            # the floor
NEED_COLORS = (0xFF6000, 0xFF2080, 0x2040FF)  # A shows: food, love, sleep
FEED_SONG = [(523, 0.08), (659, 0.08), (523, 0.08), (659, 0.08)]  # nom nom
PET_SONG = [(392, 0.12), (523, 0.12), (784, 0.2)]
CLEAN_SONG = [(1047, 0.05), (1319, 0.05), (1568, 0.05), (2093, 0.1)]
ASK_SONG = [(1568, 0.06), (0, 0.08), (1568, 0.06)]   # "I need something!"
NO_SONG = [(330, 0.1), (262, 0.15)]                   # "I'm full"

# ---- How it behaves (grown-ups) ----------------------------------------------
HUNGRY_AFTER = 10           # minutes from full to empty
LONELY_AFTER = 8
TIRED_AFTER = 20
SLEEP_REFILL = 3            # minutes of sleep from empty to full
FEED = 34                   # how much one snack fills (100 = full)
PET = 34                    # how much one pat fills
LOW = 34                    # asks for help at or below this
SICK_AFTER = 3              # minutes with an empty need before it gets sick
POOP_AFTER = 60             # seconds after eating
POOP_SICK_AFTER = 5         # minutes of poop left around before it gets sick
WAKE_HUNGRY = 15            # how much hungrier it is after being switched off
ASK_EVERY = 60              # seconds between chirps while it needs something
TIME_SPEED = 1              # 10 makes needs change 10x faster, for testing
SAVE_MINUTES = 2            # how often needs are saved (saving wears the flash)
SHAKE_STRENGTH = 25
DARK_FRACTION = 0.2         # dark = under 20% of the room's light...
DARK_SECONDS = 3            # ...for this long, then it sleeps
BEDTIME = 70                # only goes to bed in the dark when sleep is under this
FRAME_SECONDS = 0.5         # how long each animation frame shows
BLINK_EVERY = 4             # seconds between blinks, about
WALK_SPEED = 2              # steps per frame while walking
SHOW_NEEDS_TEXT = True      # small "food love sleep" numbers in the corner
BRIGHTNESS = 0.2
# ----------------------------------------------------------------------------

PICTURE = "pet_sprites.bmp"
CELL = 24                   # each frame is 24x24 pixels in the picture
SCALE = 6                   # the pet is drawn 6x: 144x144 on the screen
PROP_SCALE = 4              # food, hearts, Zs and poop are drawn 4x
FLOOR_Y = 216
PET_Y = FLOOR_Y - CELL * SCALE
MIDDLE = (240 - CELL * SCALE) // 2
SUIT = 2                    # palette color of the suit (tools/pet_frames.py)
# The frames in the picture, left to right (tools/pet_frames.py makes them).
FRAMES = ["idle0", "idle1", "blink", "walk0", "walk1", "eat0", "eat1",
          "happy0", "happy1", "sad0", "sad1", "sick0", "sick1",
          "sleep0", "sleep1", "apple", "apple_bite", "apple_core", "heart",
          "z", "poop"]
ANIMATIONS = {"idle": ("idle0", "idle1"), "walk": ("walk0", "walk1"),
              "eat": ("eat0", "eat1"), "happy": ("happy0", "happy1"),
              "sad": ("sad0", "sad1"), "sick": ("sick0", "sick1"),
              "sleep": ("sleep0", "sleep1"), "doze": ("sleep0", "sleep1")}
MOOD_LIGHTS = {"idle": 0xCB0002, "walk": 0xCB0002, "eat": 0xFF6000,
               "happy": 0xFF2080, "sad": 0x2040FF, "sick": 0x40C000,
               "sleep": 0x100020, "doze": 0x2040FF}
NEED_PROPS = ("apple", "heart", "z")     # what it asks for, by need
SAVE_FORMAT = "<4sBBBBBB"
SAVE_MAGIC = b"PET1"
NEED_PIXELS = ((0, 1, 2), (3, 4, 5), (6, 7, 8))  # 9: health


def paint(color):
    p = displayio.Palette(1)
    p[0] = color
    return p


def song(notes):
    for freq, seconds in notes:
        if freq:
            common.beep(freq, seconds)
        else:
            time.sleep(seconds)


def dim(color, level):
    return tuple(int(((color >> s) & 0xFF) * level) for s in (16, 8, 0))


class Pet:
    """The pet, a prop next to it, the poop, the sky and the grass."""

    def __init__(self):
        import adafruit_imageload
        sheet, self.palette = adafruit_imageload.load(
            PICTURE, bitmap=displayio.Bitmap, palette=displayio.Palette)
        self.palette.make_transparent(0)
        self.root = displayio.Group()
        self.sky = paint(SKY)
        self.root.append(vectorio.Rectangle(pixel_shader=self.sky, width=240,
                                            height=FLOOR_Y, x=0, y=0))
        self.root.append(vectorio.Rectangle(pixel_shader=paint(GRASS), width=240,
                                            height=240 - FLOOR_Y, x=0, y=FLOOR_Y))

        def sprite(scale):
            grid = displayio.TileGrid(sheet, pixel_shader=self.palette,
                                      tile_width=CELL, tile_height=CELL)
            group = displayio.Group(scale=scale)
            group.append(grid)
            group.hidden = True
            self.root.append(group)
            return [group, grid, None]

        self.body = sprite(SCALE)
        self.props = [sprite(PROP_SCALE), sprite(PROP_SCALE)]  # [thing, poop]
        self.body[0].hidden = False
        self.body[0].x, self.body[0].y = MIDDLE, PET_Y
        self.text = label.Label(terminalio.FONT, text="", color=0xFFFFFF, x=4, y=8)
        self.text.hidden = not SHOW_NEEDS_TEXT
        self.root.append(self.text)

    @staticmethod
    def _frame(sprite, name):
        if name != sprite[2]:
            sprite[1][0] = FRAMES.index(name)
            sprite[2] = name

    def show(self, frame, x, y=PET_Y, left=False):
        self._frame(self.body, frame)
        self.body[1].flip_x = left
        self.body[0].x, self.body[0].y = x, y

    def show_prop(self, slot, name, x=0, y=0):
        """Show a prop with its middle at x, y, or hide it (name None)."""
        group = self.props[slot][0]
        if name is None:
            group.hidden = True
            return
        self._frame(self.props[slot], name)
        half = CELL * PROP_SCALE // 2
        group.x, group.y = x - half, y - half
        group.hidden = False

    def night(self, dark):
        self.sky[0] = NIGHT if dark else SKY

    def suit(self, color):
        self.palette[SUIT] = color


class Needs:
    """Food, love and sleep, 0 (empty) to 100 (full), plus sick and poop.
    Saved in the board's non-volatile memory, so they survive power-off."""

    def __init__(self):
        self.food = self.love = self.sleep = 100.0
        self.sick = self.poop = False
        self.scheme = 0
        self.empty_for = 0          # seconds a need has been empty
        self.poop_for = 0           # seconds the poop has been left
        self.poop_at = None         # when the next poop comes
        self.saved = None
        self.next_save = 0
        try:
            saved = bytes(microcontroller.nvm[0:struct.calcsize(SAVE_FORMAT)])
            magic, food, love, sleep, sick, poop, scheme = struct.unpack(
                SAVE_FORMAT, saved)
        except Exception:
            return
        if magic == SAVE_MAGIC:
            self.food = max(0, min(100, food) - WAKE_HUNGRY)
            self.love, self.sleep = min(100, love), min(100, sleep)
            self.sick, self.poop = bool(sick), bool(poop)
            self.scheme = scheme % len(SUIT_COLORS)

    def lowest(self):
        """(which need, how full): 0 food, 1 love, 2 sleep."""
        values = (self.food, self.love, self.sleep)
        i = values.index(min(values))
        return i, values[i]

    def update(self, seconds, asleep, now):
        t = seconds * TIME_SPEED
        slow = 0.5 if asleep else 1     # needs drop slower while it sleeps
        self.food = max(0, self.food - t * slow * 100 / (HUNGRY_AFTER * 60))
        self.love = max(0, self.love - t * slow * 100 / (LONELY_AFTER * 60))
        if asleep:
            self.sleep = min(100, self.sleep + t * 100 / (SLEEP_REFILL * 60))
        else:
            self.sleep = max(0, self.sleep - t * 100 / (TIRED_AFTER * 60))
        self.empty_for = self.empty_for + t if self.lowest()[1] <= 0 else 0
        if self.poop_at is not None and now >= self.poop_at:
            self.poop, self.poop_at = True, None
        self.poop_for = self.poop_for + t if self.poop else 0
        if (self.empty_for > SICK_AFTER * 60
                or self.poop_for > POOP_SICK_AFTER * 60):
            self.sick = True

    def save(self, now, force=False):
        if not force and now < self.next_save:
            return
        self.next_save = now + SAVE_MINUTES * 60
        data = struct.pack(SAVE_FORMAT, SAVE_MAGIC, int(self.food),
                           int(self.love), int(self.sleep), int(self.sick),
                           int(self.poop), self.scheme)
        if data != self.saved:
            microcontroller.nvm[0:len(data)] = data
            self.saved = data


def run():
    cp.pixels.brightness = BRIGHTNESS
    cp.pixels.auto_write = False
    random.seed(int(time.monotonic() * 1000))

    # Our own SPI bus, so the next start (from the launcher) doesn't fail
    # with "A4 in use".
    displayio.release_displays()
    spi = busio.SPI(board.SCL, MOSI=board.SDA)
    display = tft_gizmo.TFT_Gizmo(spi=spi)
    needs = None
    try:
        display.auto_refresh = False
        try:
            pet = Pet()
        except OSError:
            missing(display)
            return
        display.root_group = pet.root
        needs = Needs()
        play(pet, needs, display)
    finally:
        if needs:
            needs.save(0, force=True)
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


def show_needs(needs):
    """The lights as meters: 3 for food, 3 for love, 3 for sleep, and one
    for health (green, brown with poop, yellow-green when sick)."""
    cp.pixels.fill(0)
    for pixels, value, color in zip(NEED_PIXELS,
                                    (needs.food, needs.love, needs.sleep),
                                    NEED_COLORS):
        for n, p in enumerate(pixels):
            if value > n * 33.4:
                cp.pixels[p] = color
    cp.pixels[9] = 0x80FF00 if needs.sick else 0x603000 if needs.poop else 0x00FF00


def play(pet, needs, display):
    pet.suit(SUIT_COLORS[needs.scheme])
    care = []                   # [(mood, seconds)] from feeding or petting
    care_until = 0
    mood = None
    wander, wander_until = "idle", 0
    asking = None               # what it's asking for, or None
    next_ask = 0
    tick = 0                    # which frame of the animation (0 or 1)
    next_frame = 0
    next_blink = time.monotonic() + BLINK_EVERY
    x, left = MIDDLE, False
    prop_step = 0
    last_touch = 0
    lights_until = 0            # showing the needs on the lights until then
    asleep = False
    next_sense = 0
    light = room = max(1, cp.light)
    dark_since = None
    stay_awake_until = 0
    last = time.monotonic()
    shown_text = None

    while True:
        now = time.monotonic()
        needs.update(now - last, asleep, now)
        last = now
        needs.save(now)

        # ---- Buttons and touch ----
        button = common.pressed()
        if common.wants_exit(button):
            cp.stop_tone()
            return
        if button in ("A", "B") and asleep:
            button = None           # the press just wakes it up
            dark_since = None
            stay_awake_until = now + 10
        if button == "A":           # "How are you?"
            lights_until = now + 4
            common.beep(660, 0.05)
        elif button == "B":         # dress up
            needs.scheme = (needs.scheme + 1) % len(SUIT_COLORS)
            pet.suit(SUIT_COLORS[needs.scheme])
            common.beep(440 + needs.scheme * 110, 0.08)
            next_frame = 0

        if not asleep and now - last_touch > 1:
            if cp.touch_A1:
                last_touch = now
                if needs.food >= 90:
                    song(NO_SONG)
                else:
                    needs.food = min(100, needs.food + FEED)
                    care, care_until = [("eat", 4.5), ("happy", 1.5)], 0
                    if not needs.poop and needs.poop_at is None:
                        needs.poop_at = now + POOP_AFTER / TIME_SPEED
                    song(FEED_SONG)
            elif cp.touch_A2:
                last_touch = now
                needs.love = min(100, needs.love + PET)
                needs.sick = False  # a hug makes it better
                needs.empty_for = 0
                care, care_until = [("happy", 3)], 0
                song(PET_SONG)

        # ---- Sensors, ten times a second ----
        if now >= next_sense:
            next_sense = now + 0.1
            ax, ay, az = cp.acceleration
            if needs.poop and math.sqrt(ax * ax + ay * ay + az * az) > SHAKE_STRENGTH:
                needs.poop = False
                care, care_until = [("happy", 1.5)], 0
                song(CLEAN_SONG)
            light = light * 0.7 + cp.light * 0.3
            if not asleep:
                # The room's light: follows the brightest recent light,
                # slowly forgetting it, so a dimmer room becomes normal.
                room = max(room * 0.998, light, 1)
            if light < room * DARK_FRACTION and now > stay_awake_until:
                dark_since = dark_since or now
            else:
                dark_since = None
        if (not asleep and dark_since and now - dark_since > DARK_SECONDS
                and needs.sleep < BEDTIME):
            asleep = True
            care = []
            song([(330, 0.15), (262, 0.3)])
        elif asleep and (not dark_since or needs.sleep >= 100):
            # Uncovered, or rested: good morning! Rested in the dark, it
            # stays up until it's tired again (BEDTIME).
            asleep = False
            needs.sick = False      # a good sleep makes it better too
            needs.empty_for = 0
            song([(523, 0.08), (784, 0.12)])
            next_blink = now + BLINK_EVERY

        # ---- What it does now ----
        if care and care_until == 0:
            care_until = now + care[0][1]
        if care and now >= care_until:
            care.pop(0)
            care_until = now + care[0][1] if care else 0
        need, value = needs.lowest()
        ask = None
        if asleep:
            want = "sleep"
        elif care:
            want = care[0][0]
        elif needs.sick:
            want, ask = "sick", 1   # a hug (pat) makes it better
        elif needs.sleep <= LOW:
            want, ask = "doze", 2
        elif value <= LOW:
            want, ask = "sad", need
        else:
            if now >= wander_until:
                happy = min(needs.food, needs.love, needs.sleep) > 70
                wander = random.choice(["idle", "idle", "walk"]
                                       + (["happy"] if happy else []))
                wander_until = now + (2 if wander == "happy" else random.uniform(4, 8))
            want = wander
        if ask is not None and (ask != asking or now >= next_ask):
            next_ask = now + ASK_EVERY
            song(ASK_SONG)
        asking = ask

        if want != mood:
            mood = want
            tick, next_frame, prop_step = 0, 0, 0
            if mood != "walk":
                x, left = MIDDLE, False
            pet.night(mood == "sleep")

        # ---- Lights ----
        if now < lights_until:
            show_needs(needs)
        else:
            glow = 0.3 if mood in ("sleep", "doze") else 0.6
            glow += 0.3 * math.sin(now * 2)
            cp.pixels.fill(dim(MOOD_LIGHTS[mood], glow))
        cp.pixels.show()

        if now < next_frame:
            time.sleep(0.02)
            continue

        # ---- The next animation frame ----
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
        elif mood == "happy" and tick == 0:
            y = PET_Y - 2 * SCALE   # hop, arms up
        pet.show(frame, x, y, left)

        # The apple gets eaten, hearts and Zs float up, and when it needs
        # something, a picture of it bobs above its head.
        prop_step += 1
        if mood == "eat":
            bites = ["apple", "apple", "apple_bite", "apple_bite", "apple_core"]
            pet.show_prop(0, bites[min(prop_step - 1, len(bites) - 1)], x + 150, 162)
        elif mood == "happy":
            pet.show_prop(0, "heart", x + 112, 50 - 8 * (prop_step % 4))
        elif mood in ("sleep", "doze"):
            pet.show_prop(0, "z", x + 120, 90 - 12 * (prop_step % 5))
        elif asking is not None:
            pet.show_prop(0, NEED_PROPS[asking], x + 120, 40 + 6 * (prop_step % 2))
        else:
            pet.show_prop(0, None)
        pet.show_prop(1, "poop" if needs.poop else None, 22, FLOOR_Y - 12)

        if SHOW_NEEDS_TEXT:
            text = "food %d love %d sleep %d%s%s" % (
                needs.food, needs.love, needs.sleep,
                " sick" if needs.sick else "", " poop" if needs.poop else "")
            if text != shown_text:
                pet.text.text = shown_text = text
        display.refresh()
