from machine import I2C, SoftSPI, Pin
import struct
import utime
import time

def map_range(v, input_min, input_max, output_min, output_max):
    return output_min + ((v - input_min) / (input_max - input_min)) * (output_max - output_min)


# I2C
from imu import MPU6050
from fusion import Fusion


imu = MPU6050(I2C(0, sda=Pin(16), scl=Pin(17), freq=400000))
print(imu.accel.y)

fuse = Fusion()

fuse.update_nomag(imu.accel.xyz, imu.gyro.xyz)


root_start_time = time.ticks_ms()
counter = 0
time_len = 10
while time.ticks_diff(time.ticks_ms(), root_start_time) / 1000 < time_len:

    a = imu.accel.xyz
    b = imu.gyro.xyz
    fuse.update_nomag(imu.accel.xyz, imu.gyro.xyz)



# timer_2_channel_1.pulse_width_percent(int(map_range(fuse.roll, -1, 1, 0, 100)))
    # timer_2_channel_2.pulse_width_percent(int(map_range(fuse.pitch, -1, 1, 0, 100)))
    counter = counter + 1

print('freq: ', counter / time_len)
print('T: ',time_len / counter)

