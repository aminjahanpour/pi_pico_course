# importing libraries
from machine import Pin
import time

# I can have both digital input and digital output pins on my board

# the button
my_button = Pin(13, Pin.IN, Pin.PULL_UP)

# the two LEDs
first_led = Pin(14, Pin.OUT)
second_led = Pin(15, Pin.OUT)


while True:


    if my_button.value() == 0:
        # the btn is pressed
        first_led.on()
        second_led.off()

    else:
        first_led.off()
        second_led.on()

    time.sleep(0.1)     # wait 1 second



