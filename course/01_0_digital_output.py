# importing libraries
from machine import Pin
import time

# set up the onboard LED as a digital output
# the LED is hard-wired to GPIO25
led = Pin(25, Pin.OUT)


while True:

    # Toggling the board LED

    led.toggle()      # switch LED on/off

    time.sleep(1)     # wait 1 second
