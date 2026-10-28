from machine import Pin

from hcsr04 import HCSR04
from time import sleep

import time



led = Pin(25, Pin.OUT)
buzzer = Pin(15, Pin.OUT)

led.off()
buzzer.off()

t1 = 0

# Create the sensor object
sensor = HCSR04(trigger_pin=16, echo_pin=17)

while True:
    try:
        distance = sensor.distance_cm()
        #print("Distance:", round(distance, 2), "cm")



        if (distance < 20):
            t1 = t1 + 1
        
        else:
            #led.off()
            t1 = 0


        if (t1 > 20):
            led.on()
            buzzer.on()
        else:
            led.off()
            buzzer.off()



        print(t1)

    except OSError as e:
        print("Measurement error:", e)

    sleep(0.05)