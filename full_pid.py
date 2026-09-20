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
import toolkit

"""
in order to start up the ESCs we have to send a min value
of PWM to them before connecting the battery. Otherwise,
the ESCs won't start up or enter in the configureation mode.
the min value is 1000us and max is 2000us, remember.
"""

def limit_to_range(v, abs_range):
    ans = v
    if v < -abs_range:
        ans = -abs_range
    elif v > abs_range:
        ans = abs_range
    return ans

# lcd = LCD(I2C(0, sda=Pin(0), scl=Pin(1), freq=400000))


esc_3 = PWM(Pin(18))
esc_1 = PWM(Pin(17))
esc_2 = PWM(Pin(19))
esc_4 = PWM(Pin(20))

esc_3.freq(50)
esc_1.freq(50)
esc_2.freq(50)
esc_4.freq(50)

esc_min = 3276 # use when setting the PWM pin to avoid reconfiguration
esc_max = 6553 # max value used in calibration
esc_min_throttle = 3400  # minimum stable throttle such that blades rotate
esc_max_throttle = 4000  # maximum safe throttle such that the engine won't start to melt

esc_min_pid_throttle = 3400  # minimum throttle while flying
esc_max_pid_throttle = 4000   # maximum throttle while flying
esc_middle_pid_throttle = int(0.5*(esc_min_pid_throttle + esc_max_pid_throttle))

esc_3.duty_u16(int(esc_min))
esc_1.duty_u16(int(esc_min))
esc_2.duty_u16(int(esc_min))
esc_4.duty_u16(int(esc_min))


# Set up IMU
imu = MPU6050(I2C(1, sda=Pin(2), scl=Pin(3), freq=400000))
fuse = Fusion()

print('level the IMU..')
toolkit.board_led(0)
while True:
    roll_angle = imu.accel.y * 180 / 3.1415
    pitch_angle = imu.accel.x * 180 / 3.1415
    if abs(roll_angle)<1 and abs(pitch_angle)<1:
        break
fuse = Fusion()
print('done')
toolkit.board_led(1)

# sleep(2)
#
# print('initiating FUSE..')
# while True:
#     roll_angle = imu.accel.y * 180 / 3.1415
#     pitch_angle = imu.accel.x * 180 / 3.1415
#     fuse.update_nomag(imu.accel.xyz, imu.gyro.xyz)
#     print(roll_angle, fuse.roll)
#     if abs(roll_angle-fuse.roll) < 1 and abs(pitch_angle-fuse.pitch) < 1:
#         break
# print('calibration complete')
# toolkit.board_led(1)



roll_angle = imu.accel.y * 180 / 3.1415  # to degrees
pitch_angle = imu.accel.x * 180 / 3.1415  # to degrees
last_pitch_angle = copy.deepcopy(pitch_angle)
last_roll_angle = copy.deepcopy(roll_angle)


for i in range(500):
    fuse.update_nomag(imu.accel.xyz, imu.gyro.xyz)

print(f'accl_roll_angle: {roll_angle}, fuse_roll: {fuse.roll}')
print(f'accl_pitch_angle: {pitch_angle}, pitch_roll: {fuse.pitch}')



# NRF

_RX_POLL_DELAY = const(15)
_SLAVE_SEND_DELAY = const(10)
# cfg = {"spi": 0, "miso": 4, "mosi": 3, "sck": 2, "csn": 5, "ce": 6}
cfg = {"spi": 0, "miso": 4, "mosi": 7, "sck": 6, "csn": 15, "ce": 14}
pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")
csn = Pin(cfg["csn"], mode=Pin.OUT, value=1)
ce = Pin(cfg["ce"], mode=Pin.OUT, value=0)
if cfg["spi"] == -1:
    spi = SPI(-1, sck=Pin(cfg["sck"]), mosi=Pin(cfg["mosi"]), miso=Pin(cfg["miso"]))
    nrf = NRF24L01(spi, csn, ce, payload_size=8)
else:
    nrf = NRF24L01(SPI(cfg["spi"]), csn, ce, payload_size=12)

nrf.open_tx_pipe(pipes[1])
nrf.open_rx_pipe(1, pipes[0])
nrf.start_listening()
print('NRF good to go')

# SETUP MOTORS
print('connect battery')
sleep(10)

esc_1_v = copy.deepcopy(esc_middle_pid_throttle)
esc_2_v = copy.deepcopy(esc_middle_pid_throttle)
esc_3_v = copy.deepcopy(esc_middle_pid_throttle)
esc_4_v = copy.deepcopy(esc_middle_pid_throttle)

esc_1.duty_u16(esc_1_v)
esc_2.duty_u16(esc_2_v)
esc_3.duty_u16(esc_3_v)
esc_4.duty_u16(esc_4_v)




print(f"on esc_min_pid_throttle")
sleep(7)





# start of time control
last_time = time.ticks_ms()
root_start_time = time.ticks_ms()

counter = 0
total_time = 0.00001

pid_p_roll = 0
pid_i_roll = 0
pid_d_roll = 0
pid_roll = 0

pid_p_pitch = 0
pid_i_pitch = 0
pid_d_pitch = 0
pid_pitch = 0


f = open('data.csv', 'w')

f.write('total_time,delta_time,roll_angle,pitch_angle,pid_roll,pid_pitch,esc_1_v,esc_2_v,esc_3_v,esc_4_v,freq\n')



print(f"PID...")

k_p = 0.5  # as far you are to the target, the bigger the force
k_i = 0  # it's taking too long, the longer it takes the higher the cost
k_d = 1  # you are going way too fast. slow down.

pid_i_max = 5
pid_max = 150
sample_time = 0.005

write_file = False

toolkit.board_led(0)

while time.ticks_diff(time.ticks_ms(), root_start_time) / 1000 < 5:
    fuse.update_nomag(imu.accel.xyz, imu.gyro.xyz)
toolkit.board_led(1)

while time.ticks_diff(time.ticks_ms(), root_start_time) / 1000 < 1500:
    if nrf.any():
        while nrf.any():

            buf = nrf.recv()
            v_1, v_2, v_3 = struct.unpack("iii", buf)

            k_p = (v_1/100) * 10
            k_i = (v_2/100) * 1
            k_d = (v_3/100) * 10

            # if counter % 100 ==0:
            #     print(k_p, k_i, k_d)

            utime.sleep_ms(_RX_POLL_DELAY)
            utime.sleep_ms(_SLAVE_SEND_DELAY)
            nrf.start_listening()

    fuse.update_nomag(imu.accel.xyz, imu.gyro.xyz)

    roll_angle = fuse.roll
    pitch_angle = fuse.pitch

    current_time = time.ticks_ms()
    delta_time = time.ticks_diff(current_time, last_time) / 1000
    delta_roll_angle = roll_angle - last_roll_angle
    delta_pitch_angle = pitch_angle - last_pitch_angle


    if delta_time >= sample_time:

        # ROLL
        pid_p_roll = k_p * roll_angle
        pid_i_roll += k_i * roll_angle * delta_time
        pid_d_roll = k_d * delta_roll_angle / delta_time if delta_time > 0 else 0

        pid_i_roll = limit_to_range(pid_i_roll, pid_i_max)

        pid_roll = pid_p_roll + pid_i_roll + pid_d_roll

        pid_roll = limit_to_range(pid_roll, pid_max)

        # PITCH
        pid_p_pitch = k_p * pitch_angle
        pid_i_pitch += k_i * pitch_angle * delta_time
        pid_d_pitch = k_d * delta_pitch_angle / delta_time if delta_time > 0 else 0

        pid_i_pitch = limit_to_range(pid_i_pitch, pid_i_max)

        pid_pitch = pid_p_pitch + pid_i_pitch + pid_d_pitch

        pid_pitch = limit_to_range(pid_pitch, pid_max)


        # remember last values
        last_time = time.ticks_ms()
        last_roll_angle = copy.deepcopy(roll_angle)
        last_pitch_angle = copy.deepcopy(pitch_angle)
        total_time += delta_time


        # APPLY
        esc_1_v = esc_1_v + pid_roll + pid_pitch
        esc_2_v = esc_2_v - pid_roll - pid_pitch
        esc_3_v = esc_3_v - pid_roll + pid_pitch
        esc_4_v = esc_4_v + pid_roll - pid_pitch

        esc_1_v = min(max(esc_1_v, esc_min_pid_throttle), esc_max_pid_throttle)
        esc_2_v = min(max(esc_2_v, esc_min_pid_throttle), esc_max_pid_throttle)
        esc_3_v = min(max(esc_3_v, esc_min_pid_throttle), esc_max_pid_throttle)
        esc_4_v = min(max(esc_4_v, esc_min_pid_throttle), esc_max_pid_throttle)

        esc_1.duty_u16(int(esc_1_v))
        esc_2.duty_u16(int(esc_2_v))
        esc_3.duty_u16(int(esc_3_v))
        esc_4.duty_u16(int(esc_4_v))

        if write_file:
            f.write(
                f'{total_time}, {delta_time}, {roll_angle}, {pitch_angle}, {pid_roll}, {pid_pitch}, {esc_1_v}, {esc_2_v}, {esc_3_v}, {esc_4_v}, {counter / total_time}\n')

        counter = counter + 1

    # else:
    #     print('skipping')

esc_1.duty_u16(esc_min_throttle)
esc_2.duty_u16(esc_min_throttle)
esc_3.duty_u16(esc_min_throttle)
esc_4.duty_u16(esc_min_throttle)

f.close()

print('over')
