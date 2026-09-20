import utime
from utime import sleep
from machine import Pin, I2C, PWM, SPI
from lcd1602 import LCD
from lib import copy
from nrf24l01 import NRF24L01
import struct
from imu import MPU6050
from fusion import Fusion
from math import tan
import time

"""
in order to start up the ESCs we have to send a min value
of PWM to them before connecting the battery. Otherwise,
the ESCs won't start up or enter in the configureation mode.
the min value is 1000us and max is 2000us, remember.
"""
# machine.freq(125000000)
# machine.freq(270000000)

_RX_POLL_DELAY = const(15)
_SLAVE_SEND_DELAY = const(10)
# cfg = {"spi": 0, "miso": 4, "mosi": 3, "sck": 2, "csn": 5, "ce": 6}
cfg = {"spi": 0, "miso": 4, "mosi": 7, "sck": 6, "csn": 15, "ce": 14}

pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")

# lcd = LCD(I2C(0, sda=Pin(0), scl=Pin(1), freq=400000))

imu = MPU6050(I2C(1, sda=Pin(2), scl=Pin(3), freq=400000))
fuse = Fusion()

esc_front_left = PWM(Pin(18))
esc_front_right = PWM(Pin(17))
esc_back_left = PWM(Pin(19))
esc_back_right = PWM(Pin(20))

esc_front_left.freq(50)
esc_front_right.freq(50)
esc_back_left.freq(50)
esc_back_right.freq(50)

esc_min = 3276
esc_max = 6553
esc_min_throttle = 3400  # minimum stable throttle
esc_max_throttle = 4000  # maximum safe throuttle

esc_front_left.duty_u16(int(esc_min))
esc_front_right.duty_u16(int(esc_min))
esc_back_left.duty_u16(int(esc_min))
esc_back_right.duty_u16(int(esc_min))

# NRF
# csn = Pin(cfg["csn"], mode=Pin.OUT, value=1)
# ce = Pin(cfg["ce"], mode=Pin.OUT, value=0)
# if cfg["spi"] == -1:
#     spi = SPI(-1, sck=Pin(cfg["sck"]), mosi=Pin(cfg["mosi"]), miso=Pin(cfg["miso"]))
#     nrf = NRF24L01(spi, csn, ce, payload_size=8)
# else:
#     nrf = NRF24L01(SPI(cfg["spi"]), csn, ce, payload_size=12)

# nrf.open_tx_pipe(pipes[1])
# nrf.open_rx_pipe(1, pipes[0])
# nrf.start_listening()

print('connect battery')
# lcd.message(f"connect battery")
sleep(10)


# lcd.clear()

print('calibrate gyro')

qyro_y = []
while len(qyro_y) < 500:
    qyro_y.append(imu.gyro.x)
qyro_offset_y = sum(qyro_y) / len(qyro_y)
qyro_y = []
del qyro_y

print(f'qyro_offset_y: {qyro_offset_y}')

root_start_time = time.ticks_ms()

starting_angle = imu.accel.y * 180 / 3.1415  # to degrees
print(f'starting_angle: {starting_angle}')
gyro_angle_x = starting_angle
angle = starting_angle
previous_err = copy.deepcopy(angle)

# start of time control
start_time = time.ticks_ms()

counter = 0
total_time = 0.00001

pid_p = 0
pid_i = 0
pid_d = 0

f = open('data.csv', 'w')
# f.write('total_time,gyro_angle_x,accel_y,accel_y_mean,angle,height,pid_p,pid_i,pid_d,pid,esc_left_v,esc_right_v,freq\n')
f.write('total_time,gyro_angle_x,angle,pid_p,pid_i,pid_d,pid,esc_left_v,esc_right_v,freq\n')

esc_front_left_v = copy.deepcopy(esc_min_throttle)
esc_front_right_v = copy.deepcopy(esc_min_throttle)
esc_back_left_v = copy.deepcopy(esc_min_throttle)
esc_back_right_v = copy.deepcopy(esc_min_throttle)

esc_front_left.duty_u16(esc_front_left_v)
esc_front_right.duty_u16(esc_front_right_v)
esc_back_left.duty_u16(esc_back_left_v)
esc_back_right.duty_u16(esc_back_right_v)





# throttle = int(copy.deepcopy(0.5*(esc_min_throttle + esc_max_throttle)))
# esc_right.duty_u16(throttle)
# esc_left.duty_u16(throttle)


# lcd.message(f"on esc_min_throttle")
print(f"on esc_min_throttle")
sleep(30)
# lcd.clear()
# lcd.message(f"PID...")
print(f"PID...")
exit()

k_p = 0.05  # as far you are to the target, the bigger the force
k_i = 0.01  # it's taking too long, the longer it takes the higher the cost
k_d = 0.01  # you are going way too fast. slow down.

k_p = 0.05
k_i = 0.01
k_d = 0.5

pid_max = 50

write_file = True

while time.ticks_diff(time.ticks_ms(), root_start_time) / 1000 < 45:
    fuse.update_nomag(imu.accel.xyz, imu.gyro.xyz)

    # end of time control
    now = time.ticks_ms()

    dt = time.ticks_diff(now, start_time) / 1000

    # start of time control
    start_time = time.ticks_ms()

    angle = fuse.roll

    total_time += dt

    err = angle

    pid_p = k_p * err
    pid_i += k_i * 0.5 * (previous_err + err) * dt
    pid_d = k_d * (err - previous_err) / dt

    pid = pid_p + pid_i + pid_d

    if pid < - pid_max:
        pid = -pid_max
    elif pid > pid_max:
        pid = pid_max

    previous_err = copy.deepcopy(err)

    # esc_right_v = throttle + pid
    # esc_left_v = throttle - pid
    esc_right_v = esc_right_v + pid
    esc_left_v = esc_left_v - pid

    # print(esc_right_v ,pid)

    esc_right_v = min(max(esc_right_v, esc_min_throttle), esc_max_throttle)
    esc_left_v = min(max(esc_left_v, esc_min_throttle), esc_max_throttle)

    esc_right.duty_u16(int(esc_right_v))
    esc_left.duty_u16(int(esc_left_v))

    # print(esc_right_v)

    if write_file:
        # print(
        #     f'gyro_angle_x:{gyro_angle_x},accel_y:{accel_y},accel_y_mean:{accel_y_mean},angle:{angle},height:{height},freq:{counter / total_time}')

        # f.write(f'{total_time},{gyro_angle_x},{accel_y},{accel_y_mean},{angle},{height},{pid_p},{pid_i},{pid_d},{pid},{esc_left_v},{esc_right_v},{counter / total_time}\n')
        f.write(
            f'{total_time},{gyro_angle_x},{angle},{pid_p},{pid_i},{pid_d},{pid},{esc_left_v},{esc_right_v},{counter / total_time}\n')

    # counter = counter + 1

esc_right.duty_u16(esc_min_throttle)
esc_left.duty_u16(esc_min_throttle)

f.close()

# lcd.clear()
# lcd.message("over")
print('over')

sleep(1)
