import time
from adafruit_circuitplayground import cp

cp.pixels.brightness = 0.2
colors = [(255, 0, 0), (255, 120, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (150, 0, 255)]

i = 0
while True:
    if cp.button_a:
        cp.pixels.fill(colors[i % len(colors)])
        cp.play_tone(300 + 80 * (i % len(colors)), 0.15)
        i += 1
        time.sleep(0.2)
    if cp.button_b:
        cp.pixels.fill(0)
    if cp.shake(shake_threshold=20):
        for p in range(10):
            cp.pixels[p] = colors[p % len(colors)]