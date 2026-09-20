import uasyncio as asyncio
import queue
import random
from machine import SoftI2C, SoftSPI, Pin, I2C
import struct
import utime
import time
from math import asin, acos, sqrt
import gc


def bytes_toint(msb, lsb):
    '''
    Convert two bytes to signed integer (big endian)
    for little endian reverse msb, lsb arguments
    Can be used in an interrupt handler
    '''
    if not msb & 0x80:
        return msb << 8 | lsb  # +ve
    return - (((msb ^ 255) << 8) | (lsb ^ 255) + 1)


buf1 = bytearray(1)
buf2 = bytearray(2)
buf3 = bytearray(3)
buf6 = bytearray(6)

# pico
# i2c = I2C(0, sda=Pin(16), scl=Pin(17), freq=400000)

# black
i2c = SoftI2C(scl="B6", sda='B7', freq=400000)
mpu_addr = i2c.scan()[0]

i2c.readfrom_mem_into(mpu_addr, 0x75, buf1)
chip_id = int(buf1[0])
assert chip_id == mpu_addr

# wake up
buf1[0] = 0x01
i2c.writeto_mem(mpu_addr, 0x6B, buf1)

# set accel range
buf1[0] = 0x10
i2c.writeto_mem(mpu_addr, 0x1C, buf1)
# cofirm range set
i2c.readfrom_mem_into(mpu_addr, 0x1C, buf1)
assert int(buf1[0]) == 16

print(buf1)
print(int(buf1[0]))

# set gyro range
buf1[0] = 0x08
i2c.writeto_mem(mpu_addr, 0x1B, buf1)
# cofirm range set
i2c.readfrom_mem_into(mpu_addr, 0x1B, buf1)
assert int(buf1[0]) == 8


# print(buf1)
# print(int(buf1[0]))


def calibrate_acc():
    # calibrate acc
    # calibrate accel
    shots = 10000
    reads = []
    while len(reads) < shots:
        i2c.readfrom_mem_into(mpu_addr, 0x3B, buf6)
        reads.append(bytes_toint(buf6[2], buf6[3]))
    acc_starting_x = sum(reads) / len(reads)

    del reads
    gc.collect()

    reads = []
    while len(reads) < shots:
        i2c.readfrom_mem_into(mpu_addr, 0x3B, buf6)
        reads.append(-bytes_toint(buf6[0], buf6[1]))
    acc_starting_y = sum(reads) / len(reads)

    reads = []
    del reads
    gc.collect()
    
    reads = []
    while len(reads) < shots:
        i2c.readfrom_mem_into(mpu_addr, 0x3B, buf6)
        reads.append(-bytes_toint(buf6[4], buf6[5]))
    acc_starting_z = sum(reads) / len(reads)

    reads = []
    del reads
    gc.collect()
    

    print(f'acc_starting_x: {acc_starting_x},\n acc_starting_y: {acc_starting_y},\n acc_starting_z: {acc_starting_z + 4096}')

calibrate_acc()


while True:
    i2c.readfrom_mem_into(mpu_addr, 0x3B, buf6)
    accel_y = -(bytes_toint(buf6[0], buf6[1]))
    accel_x = (bytes_toint(buf6[2], buf6[3]))
    accel_z = (bytes_toint(buf6[4], buf6[5]))

    i2c.readfrom_mem_into(mpu_addr, 0x43, buf6)
    gyro_x = bytes_toint(buf6[0], buf6[1])
    gyro_y = bytes_toint(buf6[2], buf6[3])
    gyro_z = bytes_toint(buf6[4], buf6[5])

    print(accel_x, accel_y, accel_z)

    # print(gyro_x, gyro_y, gyro_z)

    print('')

    time.sleep(.3)
#
