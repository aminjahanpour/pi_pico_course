
from machine import Pin, PWM
import time

# RGB LED (Common Cathode)
red = PWM(Pin(21))
green = PWM(Pin(20))
blue = PWM(Pin(19))

# Set PWM frequency
red.freq(1000)
green.freq(1000)
blue.freq(1000)

def color(r, g, b):
    # Values range from 0 to 65535
    red.duty_u16(r)
    green.duty_u16(g)
    blue.duty_u16(b)

def off():
    color(0, 0, 0)

def fade(start, end, duration=0.01):
    steps = 100

    for i in range(steps + 1):
        r = int(start[0] + (end[0] - start[0]) * i / steps)
        g = int(start[1] + (end[1] - start[1]) * i / steps)
        b = int(start[2] + (end[2] - start[2]) * i / steps)

        color(r, g, b)
        time.sleep(duration)

def dance():
    # Brightness levels
    MAX = 65535
    OFF = 0

    # Color sequence
    colors = [
        (MAX, OFF, OFF),       # Red
        (MAX, MAX, OFF),       # Yellow
        (OFF, MAX, OFF),       # Green
        (OFF, MAX, MAX),       # Cyan
        (OFF, OFF, MAX),       # Blue
        (MAX, OFF, MAX),       # Magenta
        (MAX, MAX, MAX),       # White
        (MAX, OFF, OFF)        # Back to red
    ]

    for i in range(len(colors) - 1):
        fade(colors[i], colors[i + 1])

while True:
    dance()
