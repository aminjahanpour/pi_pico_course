import machine
import utime
import urandom
from machine import Pin, ADC
import _thread

# greeting
board_led = Pin(25, Pin.OUT)
board_led(1)
utime.sleep(3)
board_led(0)
