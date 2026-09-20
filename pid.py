from imu import MPU6050
from utime import sleep
from machine import Pin, I2C, PWM
import time
from lcd1602 import LCD
from lib import copy, toolkit

from math import tan

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

esc_right = PWM(Pin(15))
esc_left = PWM(Pin(14))
esc_right.freq(50)
esc_left.freq(50)

v_max = int(0.07 * pow(2, 16))
v_min = int(0.05 * pow(2, 16))
v_initiate = int(0.06 * pow(2, 16))

engine_run = True


def calibrate_esc():
    lcd.message("calibrating in 5 secs")
    sleep(5)

    esc_right.duty_u16(v_max)
    esc_left.duty_u16(v_max)
    lcd.clear()
    lcd.message(f"v={v_max}")

    sleep(5)

    esc_right.duty_u16(v_min)
    esc_left.duty_u16(v_min)
    lcd.clear()
    lcd.message(f"v={v_min}")

    sleep(6)

    lcd.clear()


def initiate_esc():
    esc_right.duty_u16(v_min)
    esc_left.duty_u16(v_min)

    lcd.clear()
    lcd.message("connect the battery now")

    sleep(20)
    lcd.clear()


if engine_run:
    toolkit.board_led.on()
    # calibrate_esc()
    # initiate_esc()
    toolkit.board_led.off()


def map_range(v, input_min, input_max, output_min, output_max):
    return output_min + ((v - input_min) / (input_max - input_min)) * (output_max - output_min)


# calibrate gyro

qyro_y = []
while len(qyro_y) < 500:
    qyro_y.append(imu.gyro.x)
qyro_offset_y = sum(qyro_y) / len(qyro_y)
qyro_y = []
del qyro_y


print(f'qyro_offset_y: {qyro_offset_y}')

root_start_time = time.ticks_ms()


starting_angle = imu.accel.y * 180 / 3.1415  # to degrees

gyro_angle_x = starting_angle
angle = starting_angle

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
accel_ys = accel_rolling_len * [starting_angle]

f = open('data.csv', 'w')
f.write('total_time,gyro_angle_x,accel_y,accel_y_mean,angle,height,pid_p,pid_i,pid_d,pid,esc_left_v,esc_right_v,freq\n')

lcd.clear()
lcd.message("go")

throttle = copy.deepcopy(v_initiate)
esc_right.duty_u16(throttle)
print('esc_right going...')
# esc_left.duty_u16(throttle)

# while True:
#     sleep(5)
#     throttle = throttle * 1.05
#     esc_right.duty_u16(throttle)
#     print(throttle)

while time.ticks_diff(time.ticks_ms(), root_start_time) / 1000 < 450:
    # while True:

    x, y, z = imu.accel.xyz  # in radian

    accel_y = y * 180 / 3.1415  # degrees

    accel_ys.append(accel_y)
    accel_ys.pop(0)
    accel_y_mean = sum(accel_ys) / len(accel_ys)

    gyro_x_rate = imu.gyro.x - qyro_offset_y  # roll rate as degree per second

    # end of time control
    now = time.ticks_ms()

    dt = time.ticks_diff(now, start_time) / 1000

    # start of time control
    start_time = time.ticks_ms()

    gyro_angle_x += gyro_x_rate * dt  # degrees

    angle = gyro_part * (angle + (gyro_x_rate * dt)) + acc_part * accel_y_mean

    total_time += dt


    # PID
    height = tan(angle * 3.1415 / 180) * 44.45

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
        sleep(0.3)



    if not engine_run:
        print(
            f'gyro_angle_x:{gyro_angle_x},accel_y:{accel_y},accel_y_mean:{accel_y_mean},angle:{angle},height:{height},freq:{counter / total_time}')

    f.write(f'{total_time},{gyro_angle_x},{accel_y},{accel_y_mean},{angle},{height},{pid_p},{pid_i},{pid_d},{pid},{esc_left_v},{esc_right_v},{counter / total_time}\n')

    counter = counter + 1






esc_right.duty_u16(v_min)
esc_left.duty_u16(v_min)

f.close()

lcd.clear()
lcd.message("over")

sleep(1)









