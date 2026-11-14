
from machine import Pin
import time

# RGB LED (Common Cathode)
red = Pin(21, Pin.OUT)
green = Pin(20, Pin.OUT)
blue = Pin(19, Pin.OUT)

def color(r, g, b):
    red.value(r)
    green.value(g)
    blue.value(b)

def off():
    color(0, 0, 0)

def dance():
    # Individual colours
    color(1, 0, 0)
    time.sleep(0.3)

    color(0, 1, 0)
    time.sleep(0.3)

    color(0, 0, 1)
    time.sleep(0.3)

    # Colour combinations
    color(1, 1, 0)  # Yellow
    time.sleep(0.3)

    color(0, 1, 1)  # Cyan
    time.sleep(0.3)

    color(1, 0, 1)  # Magenta
    time.sleep(0.3)

    color(1, 1, 1)  # White
    time.sleep(0.5)

    # Alternating dance
    for i in range(4):
        color(1, 0, 0)
        time.sleep(0.12)
        color(0, 1, 0)
        time.sleep(0.12)
        color(0, 0, 1)
        time.sleep(0.12)

    # Two-colour party
    for i in range(3):
        color(1, 1, 0)
        time.sleep(0.2)
        color(0, 1, 1)
        time.sleep(0.2)
        color(1, 0, 1)
        time.sleep(0.2)

    # Rapid flashing
    for i in range(6):
        color(1, 1, 1)
        time.sleep(0.1)
        off()
        time.sleep(0.1)

    # Grand finale
    color(1, 0, 1)
    time.sleep(0.5)
    color(0, 1, 1)
    time.sleep(0.5)
    color(1, 1, 0)
    time.sleep(0.5)
    color(1, 1, 1)
    time.sleep(1)

    off()
    time.sleep(0.5)


while True:
    dance()

