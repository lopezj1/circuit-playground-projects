# Launcher: every game on one board.
#
# A:   next game (each game has its own color)
# B:   start the game
# A+B: inside a game, back to this menu
#
# Games are loaded only when started and unloaded afterwards, so the board
# doesn't run out of memory as more games get added.
import gc
import sys
import time
from adafruit_circuitplayground import cp
import common

# ---- Kid's choices ---------------------------------------------------------
# (module name, menu color, menu tone). Add a new game with one line here.
GAMES = [
    ("game_wand", (150, 0, 255), 523),    # purple
    ("game_piano", (0, 255, 0), 659),     # green
    ("game_dice", (255, 200, 0), 784),    # yellow
    ("game_halloween", (255, 80, 0), 392),  # pumpkin orange
]
BRIGHTNESS = 0.2
# ----------------------------------------------------------------------------

common.in_launcher = True


def reset_board():
    cp.stop_tone()
    cp.pixels.auto_write = True
    cp.pixels.brightness = BRIGHTNESS
    cp.pixels.fill(0)


def show_choice(index):
    _, color, tone = GAMES[index]
    cp.pixels.fill(0)
    for p in range(index + 1):      # one bright pixel per game number
        cp.pixels[p] = color
    common.beep(tone, 0.1)


def start_game(index):
    name, color, tone = GAMES[index]
    cp.pixels.fill(color)
    common.beep(tone, 0.08)
    common.beep(tone * 2, 0.12)
    gc.collect()
    print("start", name, "free memory:", gc.mem_free())
    try:
        game = __import__(name)
        game.run()
    except Exception as e:          # show red instead of crashing the menu
        print("error in", name + ":", e)
        cp.pixels.fill((255, 0, 0))
        common.beep(200, 0.5)
        time.sleep(1)
    reset_board()
    game = None
    if name in sys.modules:
        del sys.modules[name]
    gc.collect()
    print("back to menu, free memory:", gc.mem_free())


reset_board()
choice = 0
show_choice(choice)
glow = 0.3
glow_up = True

while True:
    button = common.pressed()
    if button == "A":
        choice = (choice + 1) % len(GAMES)
        show_choice(choice)
    elif button == "B":
        start_game(choice)
        show_choice(choice)

    # The chosen game's pixels breathe so it's clear the menu is waiting.
    glow += 0.01 if glow_up else -0.01
    if glow >= 0.3:
        glow_up = False
    elif glow <= 0.05:
        glow_up = True
    cp.pixels.brightness = glow
    time.sleep(0.02)
