import uasyncio as asyncio
import queue
import random
from machine import SoftI2C, SoftSPI, Pin, I2C
import struct
import utime
import time

from imu import MPU6050
from fusion import Fusion
import gc
from math import sin

root_start_time = time.ticks_ms()

a= 1.001
for i in range(200000):
    
    # a = pow(a, 2)
    a = a ** 1.2

print(time.ticks_diff(time.ticks_ms(), root_start_time) / 1000)

"""
ts = time_ticks_us()
dt = time.ticks_diff(ts, start_time) / 1000000
start_time = ts

"""