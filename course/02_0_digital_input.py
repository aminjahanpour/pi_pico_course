from machine import Pin
import time


# set up GPIO13 as a digital input.
# the set the pin to be internally pulled high
my_button = Pin(13, Pin.IN, Pin.PULL_UP)


while True:

    if my_button.value() == 0:
        # the pin is grounded
        print(0)

    else:
        # the pin is not grounded.
        print(1)

    time.sleep(0.1)