from machine import Pin
import time


# set up GPIO14 as a digital input.
# the set the pin to be internally pulled high
gpio14 = Pin(14, Pin.IN, Pin.PULL_UP)


while True:

    if gpio14.value() == 0:
        # the pin is grounded
        print(0)

    else:
        # the pin is not grounded.
        print(1)

    time.sleep(0.1)