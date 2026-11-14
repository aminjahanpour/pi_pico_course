
from machine import Pin
import time

# PIR motion sensor
pir = Pin(17, Pin.IN)

# Onboard LED
led = Pin("LED", Pin.OUT)

print("Initializing PIR sensor...")

# Allow sensor to stabilize
time.sleep(10)

print("PIR sensor ready!")

while True:

    if pir.value() == 1:
        print("Motion detected!")
        led.on()

    else:
        print("No motion")
        led.off()

    time.sleep(0.2)

