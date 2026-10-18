# 03 Dice: shake or press A to roll. The lights show the number and it
# beeps once per pixel so you can count along.
#
# Shake or A: roll
# B:          switch between a 6-sided die and a 10-sided die
# A+B:        back to the menu (in the launcher)
# Slide switch: sound on / off
import random
import time
from adafruit_circuitplayground import cp
import common

# ---- Kid's choices ---------------------------------------------------------
# Color for each number (1 through 10)
NUMBER_COLORS = [
    (255, 0, 0),      # 1 red
    (255, 120, 0),    # 2 orange
    (255, 255, 0),    # 3 yellow
    (0, 255, 0),      # 4 green
    (0, 200, 255),    # 5 light blue
    (0, 0, 255),      # 6 blue
    (150, 0, 255),    # 7 purple
    (255, 0, 150),    # 8 pink
    (255, 255, 255),  # 9 white
    (120, 255, 120),  # 10 mint
]
SPIN_COLOR = (255, 255, 255)
SHAKE_STRENGTH = 20
BRIGHTNESS = 0.2
# ----------------------------------------------------------------------------


def roll(sides):
    # Spin around the ring, slowing down like a wheel.
    delay = 0.02
    p = 0
    while delay < 0.15:
        if common.exit_held():
            return
        cp.pixels.fill(0)
        cp.pixels[p % 10] = SPIN_COLOR
        common.beep(1200, 0.01)
        time.sleep(delay)
        delay *= 1.12
        p += 1

    number = random.randint(1, sides)
    color = NUMBER_COLORS[number - 1]

    # Count up one pixel at a time so they can count along.
    cp.pixels.fill(0)
    time.sleep(0.3)
    for i in range(number):
        if common.exit_held():
            return
        cp.pixels[i] = color
        common.beep(400 + i * 80, 0.15)
        time.sleep(0.25)
    common.beep(1000, 0.3)


def show_sides(sides):
    cp.pixels.fill(0)
    for i in range(sides):
        cp.pixels[i] = (40, 40, 40)
    common.beep(500 if sides == 6 else 800, 0.15)


def run():
    cp.pixels.brightness = BRIGHTNESS
    random.seed(int(time.monotonic() * 1000))
    sides = 6
    show_sides(sides)

    while True:
        button = common.pressed()
        if common.wants_exit(button):
            return
        if button == "A" or cp.shake(shake_threshold=SHAKE_STRENGTH):
            roll(sides)
        elif button == "B":
            sides = 10 if sides == 6 else 6
            show_sides(sides)

        time.sleep(0.02)
