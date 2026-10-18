# 01 Wand: shake to cast a spell.
#
# Shake: cast the current spell (lights + sound)
# A:     pick the next spell
# B:     lights out
# Slide switch: sound on / off
import time
from adafruit_circuitplayground import cp

# ---- Kid's choices ---------------------------------------------------------
FAVORITE = (150, 0, 255)          # the wand's resting glow color
RAINBOW = [
    (255, 0, 0),      # red
    (255, 120, 0),    # orange
    (255, 255, 0),    # yellow
    (0, 255, 0),      # green
    (0, 0, 255),      # blue
    (150, 0, 255),    # purple
]
SPELLS = ["rainbow", "sparkle", "favorite"]
SHAKE_STRENGTH = 20               # lower = easier to trigger
BRIGHTNESS = 0.2
# ----------------------------------------------------------------------------

cp.pixels.brightness = BRIGHTNESS
cp.pixels.auto_write = False


def beep(freq, seconds):
    if cp.switch:
        cp.play_tone(freq, seconds)
    else:
        time.sleep(seconds)


def dim(color, amount):
    return tuple(int(c * amount) for c in color)


def spell_rainbow():
    for step in range(20):
        for p in range(10):
            cp.pixels[p] = RAINBOW[(p + step) % len(RAINBOW)]
        cp.pixels.show()
        beep(400 + step * 40, 0.04)


def spell_sparkle():
    seed = 7
    for step in range(25):
        cp.pixels.fill(0)
        seed = (seed * 31 + 17) % 101
        cp.pixels[seed % 10] = (255, 255, 255)
        cp.pixels[(seed // 10) % 10] = RAINBOW[step % len(RAINBOW)]
        cp.pixels.show()
        beep(900 + (seed % 5) * 150, 0.03)


def spell_favorite():
    for p in range(10):
        cp.pixels[p] = FAVORITE
        cp.pixels.show()
        beep(500 + p * 60, 0.05)
    beep(1100, 0.2)


SPELL_FUNCS = {
    "rainbow": spell_rainbow,
    "sparkle": spell_sparkle,
    "favorite": spell_favorite,
}


def fade_out():
    for level in range(10, -1, -1):
        cp.pixels.brightness = BRIGHTNESS * level / 10
        cp.pixels.show()
        time.sleep(0.05)
    cp.pixels.fill(0)
    cp.pixels.brightness = BRIGHTNESS
    cp.pixels.show()


def show_spell_choice(index):
    # Light up one pixel per spell number, in the favorite color.
    cp.pixels.fill(0)
    for p in range(index + 1):
        cp.pixels[p] = FAVORITE
    cp.pixels.show()
    beep(600 + index * 200, 0.1)


spell = 0
lights_on = True
glow = 0.0
glow_up = True

while True:
    if cp.button_a:
        spell = (spell + 1) % len(SPELLS)
        show_spell_choice(spell)
        lights_on = True
        while cp.button_a:
            pass
        time.sleep(0.4)

    if cp.button_b:
        lights_on = False
        cp.pixels.fill(0)
        cp.pixels.show()
        while cp.button_b:
            pass

    if cp.shake(shake_threshold=SHAKE_STRENGTH):
        lights_on = True
        SPELL_FUNCS[SPELLS[spell]]()
        fade_out()

    # Gentle breathing glow while waiting.
    if lights_on:
        glow += 0.02 if glow_up else -0.02
        if glow >= 0.4:
            glow_up = False
        elif glow <= 0.05:
            glow_up = True
        cp.pixels.fill(dim(FAVORITE, glow))
        cp.pixels.show()
    time.sleep(0.02)
