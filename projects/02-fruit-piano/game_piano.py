# 02 Fruit piano: touch a pad (or a fruit clipped to it) to play a note.
#
# Pads A1-A6 and TX are the 7 keys (A0 is the speaker, not a key).
# A:   switch between low and high notes
# B:   play "Twinkle Twinkle" so they can try to copy it
# A+B: back to the menu (in the launcher)
# Slide switch: sound on / off
import time
from adafruit_circuitplayground import cp
import common

# ---- Kid's choices ---------------------------------------------------------
# One entry per pad: (pad name, note frequency, color)
KEYS = [
    ("A1", 262, (255, 0, 0)),      # C  red
    ("A2", 294, (255, 120, 0)),    # D  orange
    ("A3", 330, (255, 255, 0)),    # E  yellow
    ("A4", 349, (0, 255, 0)),      # F  green
    ("A5", 392, (0, 200, 255)),    # G  light blue
    ("A6", 440, (0, 0, 255)),      # A  blue
    ("TX", 494, (150, 0, 255)),    # B  purple
]
TOUCH_ADJUST = 0      # raise (e.g. 100) if pads trigger by themselves
BRIGHTNESS = 0.2
# Twinkle Twinkle, as pad numbers (0 = A1 ... 6 = TX)
SONG = [0, 0, 4, 4, 5, 5, 4, 3, 3, 2, 2, 1, 1, 0]
# ----------------------------------------------------------------------------


def pad_touched(name):
    return getattr(cp, "touch_" + name)


def play_song(octave):
    for i, key in enumerate(SONG):
        if common.exit_held():
            break
        _, freq, color = KEYS[key]
        cp.pixels.fill(color)
        common.beep(freq * octave, 0.6 if i % 7 == 6 else 0.3)
        cp.pixels.fill(0)
        time.sleep(0.05)


def run():
    cp.pixels.brightness = BRIGHTNESS
    # The threshold change adds up, so only apply it once per power-up
    # (the launcher can start this game many times).
    if TOUCH_ADJUST and not getattr(common, "touch_adjusted", False):
        cp.adjust_touch_threshold(TOUCH_ADJUST)
        common.touch_adjusted = True

    octave = 1     # 1 = normal, 2 = high
    playing = None

    while True:
        button = common.pressed()
        if common.wants_exit(button):
            cp.stop_tone()
            return
        if button == "A":
            octave = 2 if octave == 1 else 1
            cp.pixels.fill((255, 255, 255) if octave == 2 else (40, 40, 40))
            time.sleep(0.3)
            cp.pixels.fill(0)
        elif button == "B":
            cp.stop_tone()
            playing = None
            play_song(octave)

        touched = None
        for i, (name, _, _) in enumerate(KEYS):
            if pad_touched(name):
                touched = i
                break

        if touched != playing:
            cp.stop_tone()
            if touched is None:
                cp.pixels.fill(0)
            else:
                _, freq, color = KEYS[touched]
                cp.pixels.fill(color)
                if cp.switch:
                    cp.start_tone(freq * octave)
            playing = touched

        time.sleep(0.01)
