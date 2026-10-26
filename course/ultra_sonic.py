from hcsr04 import HCSR04
from time import sleep

# Create the sensor object
sensor = HCSR04(trigger_pin=15, echo_pin=14)

while True:
    try:
        distance = sensor.distance_cm()
        print("Distance:", round(distance, 2), "cm")

    except OSError as e:
        print("Measurement error:", e)

    sleep(0.5)