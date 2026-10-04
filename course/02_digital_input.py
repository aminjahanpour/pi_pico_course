from machine import Pin
import time


# set up GPIO14 as a digital input.
gpio14 = Pin(14, Pin.IN, Pin.PULL_UP)


while True:
    

    if gpio14.value() == 0:
        print(1)
    else:
        print(0)

    time.sleep(0.1)