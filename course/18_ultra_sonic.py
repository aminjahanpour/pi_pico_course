from machine import Pin

from hcsr04 import HCSR04
from time import sleep

led = Pin(25, Pin.OUT)


# Create the sensor object
sensor = HCSR04(trigger_pin=16, echo_pin=17)

while True:
    try:
        distance = sensor.distance_cm()
        print("Distance:", round(distance, 2), "cm")

        if (distance > 20):
            led.on()
        else:
            led.off()


    except OSError as e:
        print("Measurement error:", e)

    sleep(0.05)