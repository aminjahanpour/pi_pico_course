
from machine import Pin
from uln2003 import Stepper
from time import sleep

motor = Stepper(
    Pin(2, Pin.OUT),
    Pin(3, Pin.OUT),
    Pin(4, Pin.OUT),
    Pin(5, Pin.OUT)
)

motor.rotate_by_angle(90)
sleep(1)
motor.rotate_by_angle(-90)

