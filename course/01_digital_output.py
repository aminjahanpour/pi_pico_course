# importing libraries
from machine import Pin
import time

# we are setting up two pins as digital outputs

# set up GPIO15 as a digital output.
# This is the pin on the bottom left.
gpio15 = Pin(15, Pin.OUT)

# set up the onboard LED as a digital output
# the LED is hard-wired to GPIO25
led = Pin(25, Pin.OUT)


while True:


    # Toggling the GPIO15
    
    gpio15.on()   # flip GPIO15

    time.sleep(1)     # wait 1 second

    gpio15.off()   # flip GPIO15

    time.sleep(1)     # wait 1 second




    # Toggling the board LED

    # led.toggle()      # switch LED on/off
    # time.sleep(1)     # wait 1 second
