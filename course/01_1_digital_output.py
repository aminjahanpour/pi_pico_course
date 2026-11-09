# importing libraries
from machine import Pin
import time


# set up GPIO15 as a digital output.
# This is the pin on the bottom left.
gpio15 = Pin(15, Pin.OUT)


while True:

    # Toggling the GPIO15
    
    gpio15.on()   # flip GPIO15

    time.sleep(1)     # wait 1 second

    gpio15.off()   # flip GPIO15

    time.sleep(1)     # wait 1 second

