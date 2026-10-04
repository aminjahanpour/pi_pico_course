# importing libraries
from machine import Pin
import time


# set up GPIO15 as a digital output.
# This is the pin on the bottom left.
gpio15 = Pin(15, Pin.OUT)

# set up the onboard LED as a digital output
# the LED is hard-wired to GPIO25
# led = Pin(25, Pin.OUT)


while True:
    
    gpio15.on()   # flip GPIO15

    time.sleep(1)     # wait 1 second

    gpio15.off()   # flip GPIO15

    time.sleep(1)     # wait 1 second


    # led.toggle()      # switch LED on/off
    # time.sleep(1)     # wait 1 second
