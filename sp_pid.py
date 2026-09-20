from imu import MPU6050
from utime import sleep
from machine import Pin, I2C
import time
from lcd1602 import LCD
from lib import copy

from math import tan

from fusion import Fusion

"""
in order to start up the ESCs we have to send a min value
of PWM to them before connecting the battery. Otherwise,
the ESCs won't start up or enter in the configureation mode.
the min value is 1000us and max is 2000us, remember.
"""
# machine.freq(125000000)
# machine.freq(270000000)

lcd = LCD(I2C(0, sda=Pin(0), scl=Pin(1), freq=400000))

imu = MPU6050(I2C(1, sda=Pin(2), scl=Pin(3), freq=400000))
fuse = Fusion()

engine_run = False

# calibrate gyro
qyro_x = []
while len(qyro_x) < 500:
    qyro_x.append(imu.gyro.x)
qyro_offset_x = sum(qyro_x) / len(qyro_x)
del qyro_x

qyro_y = []
while len(qyro_y) < 500:
    qyro_y.append(imu.gyro.x)
qyro_offset_y = sum(qyro_y) / len(qyro_y)
qyro_y = []
del qyro_y


print(f'qyro_offset_x: {qyro_offset_x}')
print(f'qyro_offset_y: {qyro_offset_y}')


root_start_time = time.ticks_ms()


starting_angle_x = imu.accel.y * 180 / 3.1415  # to degrees
starting_angle_y = imu.accel.x * 180 / 3.1415  # to degrees

gyro_angle_x = copy.deepcopy(starting_angle_x)
gyro_angle_y = copy.deepcopy(starting_angle_y)
angle_x = copy.deepcopy(starting_angle_x)
angle_y = copy.deepcopy(starting_angle_y)

# start of time control
start_time = time.ticks_ms()

counter = 0
total_time = 0.00001

gyro_part = 0.995
acc_part = 0.005

k_p = 10
k_i = 3
k_d = 0 #0.1

pid_p = 0
pid_i = 0
pid_d = 0

previous_err = 21 # cm which is on the floor

accel_rolling_len = 10
accel_ys = accel_rolling_len * [starting_angle_x]
accel_xs = accel_rolling_len * [starting_angle_y]

# f = open('data.csv', 'w')
# f.write('total_time,gyro_angle_x,accel_y,accel_y_mean,angle,height,pid_p,pid_i,pid_d,pid,esc_left_v,esc_right_v,freq\n')

lcd.clear()
lcd.message("go")

# throttle = copy.deepcopy(v_initiate)
# esc_right.duty_u16(throttle)
# print('esc_right going...')
# esc_left.duty_u16(throttle)

# while True:
#     sleep(5)
#     throttle = throttle * 1.05
#     esc_right.duty_u16(throttle)
#     print(throttle)

while time.ticks_diff(time.ticks_ms(), root_start_time) / 1000 < 450:
    # while True:
    fuse.update_nomag(imu.accel.xyz, imu.gyro.xyz)

    x, y, z = imu.accel.xyz  # in radian

    accel_y = y * 180 / 3.1415  # degrees
    accel_x = x * 180 / 3.1415  # degrees

    accel_ys.append(accel_y)
    accel_ys.pop(0)
    accel_y_mean = sum(accel_ys) / len(accel_ys)

    accel_xs.append(accel_x)
    accel_xs.pop(0)
    accel_x_mean = sum(accel_xs) / len(accel_xs)


    gyro_x_rate = imu.gyro.x - qyro_offset_x  # roll rate as degree per second
    gyro_y_rate = imu.gyro.y - qyro_offset_y  # roll rate as degree per second

    # end of time control
    now = time.ticks_ms()

    dt = time.ticks_diff(now, start_time) / 1000

    # start of time control
    start_time = time.ticks_ms()

    gyro_angle_x += gyro_x_rate * dt  # degrees
    gyro_angle_y += gyro_y_rate * dt  # degrees

    angle_x = gyro_part * (angle_x + (gyro_x_rate * dt)) + acc_part * accel_y_mean
    angle_y = gyro_part * (angle_y + (gyro_y_rate * dt)) + acc_part * accel_x_mean

    total_time += dt

    # PID
    height = tan(angle_x * 3.1415 / 180) * 44.45

    err = height

    pid_p = k_p * err
    pid_i += k_i * 0.5 * (previous_err + err) * dt
    pid_d = k_d * (err - previous_err) / dt

    pid = pid_p + pid_i + pid_d

    previous_err = copy.deepcopy(err)

    if engine_run:
        esc_right_v = throttle + pid
        esc_left_v = throttle - pid

        esc_right_v = min(max(esc_right_v, v_min), v_max)
        esc_left_v = min(max(esc_left_v, v_min), v_max)

        esc_right.duty_u16(int(esc_right_v))
        esc_left.duty_u16(int(esc_left_v))


    else:
        pass
        # sleep(0.3)



    if not engine_run:
        # print(f'gyro_angle_x:{gyro_angle_x},accel_y:{accel_y},accel_y_mean:{accel_y_mean},angle:{angle_x},height:{height},freq:{counter / total_time}')
        #print(f'angle_x:{angle_x},angle_y:{angle_y}')
        print(f'{round(fuse.pitch,2)}, {round(fuse.roll,2)}')
    # f.write(f'{total_time},{gyro_angle_x},{accel_y},{accel_y_mean},{angle_x},{height},{pid_p},{pid_i},{pid_d},{pid},{esc_left_v},{esc_right_v},{counter / total_time}\n')

    counter = counter + 1






# esc_right.duty_u16(v_min)
# esc_left.duty_u16(v_min)
#
# f.close()

lcd.clear()
lcd.message("over")

sleep(1)









