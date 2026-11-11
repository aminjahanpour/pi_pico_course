# importing libraries
from machine import Pin
import time

# I can have both digital input and digital output pins on my board

# the button
button_1 = Pin(12, Pin.IN, Pin.PULL_UP)
button_2 = Pin(13, Pin.IN, Pin.PULL_UP)

# the two LEDs
first_led = Pin(14, Pin.OUT)
second_led = Pin(15, Pin.OUT)


while True:

    button_1_is_pressed = button_1.value() == 0
    button_2_is_pressed = button_2.value() == 0

    both_buttons_are_pressed = button_1_is_pressed and button_2_is_pressed

    if both_buttons_are_pressed:

        for i in range(10):
            first_led.toggle()
            second_led.toggle()
            time.sleep(0.05)


    else:
        if button_1_is_pressed:
            first_led.on()
            second_led.off()

        elif button_2_is_pressed:
            first_led.off()
            second_led.on()
    
    
    print(button_1_is_pressed, button_2_is_pressed)
    time.sleep(0.1)     # wait 1 second




