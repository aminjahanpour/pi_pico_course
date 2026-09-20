from machine import SoftI2C, SoftSPI, Pin
from pyb import Timer
import struct
import utime
import time

def map_range(v, input_min, input_max, output_min, output_max):
    return output_min + ((v - input_min) / (input_max - input_min)) * (output_max - output_min)


# I2C
from imu import MPU6050
from fusion import Fusion

i2c = SoftI2C(scl="B6", sda='B7', freq=400000)
imu = MPU6050(i2c)

print('calibrating gyro')
imu.gyro.calibrate()
print('gyro calibrated')


fuse = Fusion()



# print(fuse.roll)
# print(fuse.pitch)

# SPI
# from nrf24l01 import NRF24L01
# 
# _RX_POLL_DELAY = const(15)
# _SLAVE_SEND_DELAY = const(10)
# pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")
# 
# cs = Pin("PB12", mode=Pin.OUT, value=1)
# ce = Pin("PA8", mode=Pin.OUT, value=0)
# spi = SoftSPI(sck="PB13", mosi="PB15", miso="PB14")
# nrf = NRF24L01(spi, cs, ce, payload_size=12)
# 
# nrf.open_tx_pipe(pipes[1])
# nrf.open_rx_pipe(1, pipes[0])
# nrf.start_listening()

# # LED
# led = Pin("PA0", Pin.OUT)
# led.high()
# led.low()
#
#
# # PWM
#
# pwm_pin_1 = Pin('PA0', Pin.OUT)
# pwm_pin_2 = Pin('PA1', Pin.OUT)
#
# timer_2 = Timer(2, freq=1000)
# timer_2_channel_1 = timer_2.channel(1, Timer.PWM, pin=pwm_pin_1, pulse_width_percent=0)
# timer_2_channel_2 = timer_2.channel(2, Timer.PWM, pin=pwm_pin_2, pulse_width_percent=0)
#
# timer_2_channel_1.pulse_width_percent(100)
# timer_2_channel_2.pulse_width_percent(100)





starting_roll_angle = imu.accel.y * 180 / 3.1415  # to degrees
gyro_roll_angle = starting_roll_angle
roll_angle = starting_roll_angle

starting_pitch_angle = imu.accel.x * 180 / 3.1415  # to degrees
gyro_pitch_angle = starting_pitch_angle
pitch_angle = starting_pitch_angle


accel_rolling_len = 10
accel_ys = accel_rolling_len * [starting_roll_angle]
accel_xs = accel_rolling_len * [starting_pitch_angle]

gyro_part = 0.95
acc_part = 0.05

start_time = time.ticks_ms()





root_start_time = time.ticks_ms()
counter = 0
time_len = 10
while time.ticks_diff(time.ticks_ms(), root_start_time) / 1000 < time_len:

#     now = time.ticks_ms()
#     dt = time.ticks_diff(now, start_time) / 1000
#     imu_gyro_x,imu_gyro_y,imu_gyro_z = imu.gyro.xyz
#     accel_x, accel_y, accel_z = [x*180/3.1415 for x in imu.accel.xyz]
# 
#     accel_ys.append(accel_y)
#     accel_ys.pop(0)
#     accel_y_mean = sum(accel_ys) / accel_rolling_len
# 
#     accel_xs.append(accel_x)
#     accel_xs.pop(0)
#     accel_x_mean = sum(accel_xs) / accel_rolling_len
# 
# 
#     roll_angle = gyro_part * (roll_angle + (imu_gyro_x * dt)) + acc_part * accel_y_mean
#     pitch_angle = gyro_part * (pitch_angle + (imu_gyro_y * dt)) + acc_part * accel_x_mean
# 
#     start_time = time.ticks_ms()
    
    
    
    
    a = imu.accel.xyz
    b = imu.gyro.xyz
    fuse.update_nomag(a, b)
    c=fuse.pitch
    d=fuse.roll
    # print(c, d)
    
    #print(roll_angle, pitch_angle)
    #time.sleep(0.1)
    


    counter = counter + 1

print('freq: ', counter / time_len)
print('T: ',time_len / counter)

