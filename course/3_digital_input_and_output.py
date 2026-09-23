# importing libraries
from machine import Pin
import time


# my digital input
gpio14 = Pin(14, Pin.IN, Pin.PULL_UP)

# my digital output
gpio15 = Pin(15, Pin.OUT)


while True:



    ##########################################
    # Handling digital output


    gpio15.on()   # flip GPIO15

    time.sleep(0.1)     # wait 1 second

    gpio15.off()   # flip GPIO15

    time.sleep(0.1)     # wait 1 second






    ##########################################
    # Handling digital input

    if gpio14.value() == 0:
        print(1)
    else:
        print(0)


