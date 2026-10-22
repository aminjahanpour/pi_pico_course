from hcsr04 import HCSR04
from time import sleep

sensor = HCSR04(
    trigger_pin = 16,    # Digital Output Pin
    echo_pin    = 17     # Digital Input Pin
)

while True:
    try:
        distance = sensor.distance_cm()
        print("Distance:", distance, "cm")
    except OSError as e:
        print("Measurement error:", e)

    sleep(0.1)
