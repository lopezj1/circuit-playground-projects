# Helpers shared by every game. deploy.sh copies this to the board.
import time
from adafruit_circuitplayground import cp

# The launcher sets this to True before starting a game, which turns on
# "A+B together = back to the menu". Run on its own, a game ignores A+B.
in_launcher = False


def beep(freq, seconds):
    """Play a tone, or just wait if the slide switch has sound turned off."""
    if cp.switch:
        cp.play_tone(freq, seconds)
    else:
        time.sleep(seconds)


def pressed():
    """Return "A", "B", "AB" (both at once) or None.

    Waits until the buttons are let go, so one press counts once.
    """
    a = cp.button_a
    b = cp.button_b
    if not (a or b):
        return None
    first = "A" if a else "B"
    both = a and b
    while a or b:
        a = cp.button_a
        b = cp.button_b
        if a and b:
            both = True
        time.sleep(0.01)
    return "AB" if both else first


def wants_exit(button):
    """True when the press means "back to the menu"."""
    return in_launcher and button == "AB"


def exit_held():
    """True while A+B are held in the launcher. Long animations check this
    so they can stop early; the game loop's pressed() then sees "AB"."""
    return in_launcher and cp.button_a and cp.button_b
