import uasyncio as asyncio
import queue
import random
from machine import SoftI2C, SoftSPI, Pin, I2C
import struct
import utime
import time
from nrf24l01 import NRF24L01
import copy

# from imu import MPU6050
# from fusion import Fusion
import gc
from math import asin, sqrt, atan2, sin
from pyb import Timer
from array import array
from lcd1602 import LCD

led = Pin('A15', Pin.OUT_PP,Pin.PULL_NONE)
led.high()
time.sleep(0.5)
led.low()
led = Pin('B4', Pin.OUT_PP,Pin.PULL_NONE)
led.high()
time.sleep(0.5)
led.low()




class PID():
    def __init__(self, name, k_p, k_i, k_d, min_angle_i, max_i_to_p, pid_max):
        self.name = name
        self.k_p = k_p
        self.k_i = k_i
        self.k_d = k_d
        self.min_angle_i = min_angle_i  # min angle at which I is taken into account
        self.max_i_to_p = max_i_to_p  # limit I proportionally to P
        self.pid_max = pid_max
        self.p = 0.
        self.i = 0.
        self.d = 0.
        self.pid = 0.
        self.prev_angle = 0.

    def update(self, angle, dt):
        delta_angle = angle - self.prev_angle
        self.p = self.k_p * angle
        if angle > self.min_angle_i or angle < -self.min_angle_i:
            self.i += self.k_i * 0.5 * dt * (angle + self.prev_angle)
            self.i = self.limit_to_range(self.i, abs(self.max_i_to_p * self.p))
        else:
            self.i = 0
        self.d = self.k_d * delta_angle / dt

        self.pid = self.limit_to_range(self.p + self.i + self.d, self.pid_max)

        self.prev_angle = angle

    def limit_to_range(self, v, abs_range):
        ans = v
        if v < -abs_range:
            ans = -abs_range
        elif v > abs_range:
            ans = abs_range
        return ans


def map_range(v, input_min, input_max, output_min, output_max):
    return output_min + ((v - input_min) / (input_max - input_min)) * (output_max - output_min)


def bytes_toint(msb, lsb):
    if not msb & 0x80:
        return msb << 8 | lsb  # +ve
    return - (((msb ^ 255) << 8) | (lsb ^ 255) + 1)


def calibrate_gyro(i2c, mpu_addr, buf6):
    # calibrate gyro
    shots = 1000
    reads = []
    while len(reads) < shots:
        i2c.readfrom_mem_into(mpu_addr, 0x43, buf6)
        reads.append(bytes_toint(buf6[0], buf6[1]))
    qyro_offset_x = sum(reads) / len(reads)

    del reads
    gc.collect()

    # y
    reads = []
    while len(reads) < shots:
        i2c.readfrom_mem_into(mpu_addr, 0x43, buf6)
        reads.append(bytes_toint(buf6[2], buf6[3]))
    qyro_offset_y = sum(reads) / len(reads)

    del reads
    gc.collect()

    # z
    reads = []
    while len(reads) < shots:
        i2c.readfrom_mem_into(mpu_addr, 0x43, buf6)
        reads.append(bytes_toint(buf6[4], buf6[5]))
    qyro_offset_z = sum(reads) / len(reads)

    del reads
    gc.collect()

    # calibrate accel
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

    return qyro_offset_x, qyro_offset_y, qyro_offset_z, acc_starting_x, acc_starting_y


# pico
# imu = MPU6050(I2C(0, sda=Pin(16), scl=Pin(17), freq=400000))

# blackpill
i2c = SoftI2C(scl="B6", sda='B7', freq=400000)
# imu = MPU6050(i2c)


global acc_starting_x
global acc_starting_y
acc_starting_x, acc_starting_y = (0, 0)

global imu_ready
imu_ready = False


global pos_latitude
global pos_longitude
global pos_altitude
global pos_roll
global pos_pitch
global pos_yaw

pos_latitude= 0
pos_longitude = 0
pos_altitude = 0
pos_roll = 0
pos_pitch = 0
pos_yaw = 0


"""
reference values for the flight controller PID
these are the values that the FC tries to achieve and maintain
for example if ref_roll = 5 degrees, the FC will adjust the rotors
to achieve and maintain this roll angle.
in the non-autonomous mode, the joystick will define these values.
in the autonomous mode, these values are governed by the flight computer.
these are of type integer and range of 0 to 100.
"""
global ref_throttle
global ref_roll
global ref_pitch
global ref_yaw

ref_throttle = 50
ref_roll = 0
ref_pitch = 0
ref_yaw = 0



global lcd_text
lcd_text = ''

root_start_time = time.ticks_ms()
global counter
counter = 0

asyncio_sleep_t = const(0.001)


# global param
# param = 1


async def mem_manage():  # Necessary for long term stability
    while True:
        await asyncio.sleep_ms(100)
        gc.collect()
        gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())


async def lcd_write():
    # lcd = LCD(SoftI2C(sda=Pin("B3"), scl=Pin("B10"), freq=400000))
    lcd = LCD(SoftI2C(sda=Pin("B11"), scl=Pin("B10"), freq=400000))
    lcd.clear()
    lcd.message("hi")
    while True:
        lcd.clear()
        lcd.message(lcd_text)
        # print(lcd_text)
        await asyncio.sleep(0.25)


async def nrf_non_autonomous():
    global ref_throttle
    global ref_roll
    global ref_pitch
    global ref_yaw

    global pos_latitude
    global pos_longitude
    global pos_altitude
    global pos_roll
    global pos_pitch
    global pos_yaw

    white_led = Pin('A14')
    white_led.low()
    yellow_led = Pin('A15')
    white_led.low()


    pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")

    cs = Pin("C4", mode=Pin.OUT, value=1)
    ce = Pin("C5", mode=Pin.OUT, value=0)
    spi = SoftSPI(sck="A5", mosi="A7", miso="A6")
    nrf = NRF24L01(spi, cs, ce, payload_size=12)

    nrf.open_tx_pipe(pipes[1])
    nrf.open_rx_pipe(1, pipes[0])



    while True:

        # receiving ------------------------------------------------------------------------
        nrf.start_listening()

        # wait until you receive
        while not nrf.any():
            await asyncio.sleep(asyncio_sleep_t)

        yellow_led.high()
        buf = nrf.recv()
        ref_throttle, ref_roll, ref_yaw = struct.unpack("iii", buf)

        yellow_led.low()

        nrf.stop_listening()


        # waiting ------------------------------------------------------------------------
        await asyncio.sleep(0.2)


        # sending ------------------------------------------------------------------------

        white_led.high()

        while True:
            # keep trying to send until you can
            try:
                nrf.send(struct.pack("fff", pos_roll, pos_pitch, pos_yaw))
                break
            except OSError:
                pass

        white_led.low()


async def sensor_sample(q_imu_out):
    global acc_starting_x
    global acc_starting_y
    global imu_ready

    buf1 = bytearray(1)
    buf6 = bytearray(6)

    i2c = SoftI2C(scl="B6", sda='B7', freq=400000)
    mpu_addr = i2c.scan()[0]

    i2c.readfrom_mem_into(mpu_addr, 0x75, buf1)
    chip_id = int(buf1[0])
    assert chip_id == mpu_addr

    # wake up
    buf1[0] = 0x01
    i2c.writeto_mem(mpu_addr, 0x6B, buf1)

    # set accel range  to AFS_SEL=2, divide by 4096 to get g
    buf1[0] = 0x10
    i2c.writeto_mem(mpu_addr, 0x1C, buf1)
    # cofirm range set
    i2c.readfrom_mem_into(mpu_addr, 0x1C, buf1)
    assert int(buf1[0]) == 16

    # set gyro range to FS_SEL=1, divide by 65.5 to get deg/s
    buf1[0] = 0x08
    i2c.writeto_mem(mpu_addr, 0x1B, buf1)
    # cofirm range set
    i2c.readfrom_mem_into(mpu_addr, 0x1B, buf1)
    assert int(buf1[0]) == 8

    # calibrate gyro
    qyro_offset_x, qyro_offset_y, qyro_offset_z, acc_starting_x, acc_starting_y = calibrate_gyro(i2c=i2c,
                                                                                                 mpu_addr=mpu_addr,
                                                                                                 buf6=buf6)

    """
    calculating acc offset should be done once and for when the quadcopter is perfectly balanced.
    so values for acc_offset_x and acc_offset_y are are valid only for the quadcopter.
    acc_offset_x and acc_offset_y are hard-coded here.
    We don't want to calibrate acce before each flight because we won't know if the craft would be perfectly balanced
    before each take off.    
    """
    acc_offset_x, acc_offset_y, acc_offset_z = (-3, 38, 21)
    acc_starting_x -= acc_offset_x
    acc_starting_y -= acc_offset_y

    print(f'qyro_offset x:{qyro_offset_x}, y:{qyro_offset_y}  z:{qyro_offset_z}')
    print(f'acc_starting_x x:{acc_starting_x}, y:{acc_starting_y}')

    imu_ready = True

    while True:

        try:
            # units of G
            i2c.readfrom_mem_into(mpu_addr, 0x3B, buf6)
            accel_x = bytes_toint(buf6[2], buf6[3]) - acc_offset_x
            accel_y = -bytes_toint(buf6[0], buf6[1]) - acc_offset_y
            accel_z = bytes_toint(buf6[4], buf6[5]) - acc_offset_z

            # units of deg/s
            i2c.readfrom_mem_into(mpu_addr, 0x43, buf6)
            gyro_x = bytes_toint(buf6[0], buf6[1]) - qyro_offset_x
            gyro_y = bytes_toint(buf6[2], buf6[3]) - qyro_offset_y
            gyro_z = bytes_toint(buf6[4], buf6[5]) - qyro_offset_z

            a = (accel_x, accel_y, accel_z)
            b = (gyro_x, gyro_y, gyro_z)

            await q_imu_out.put_replace((a, b))
        except OSError:
            pass

        # param = param + 1
        await asyncio.sleep(asyncio_sleep_t)


async def fusion(q_imu_out, q_fusion_out):
    global acc_starting_x
    global acc_starting_y
    global imu_ready

    # Brokking parameters
    inertia = 0.9

    # Complementary filter parameters
    gyro_part = const(0.995)
    accel_part = const(0.005)

    # Madgwick fusion parameters
    q = [1.0, 0.0, 0.0, 0.0]
    magic_param = const(80)
    beta = sqrt(3.0 / 4.0) * magic_param * 0.0174533

    # start only when imu is ready
    while not imu_ready:
        await asyncio.sleep(asyncio_sleep_t)

    print('fusion started')

    start_time = time.ticks_us()

    angle_roll_gyro = copy.deepcopy(acc_starting_x * 180 / (3.1415 * 4096))
    angle_pitch_gyro = copy.deepcopy(acc_starting_y * 180 / (3.1415 * 4096))
    angle_yaw_gyro = 0

    roll = copy.deepcopy(angle_roll_gyro)
    pitch = copy.deepcopy(angle_pitch_gyro)
    yaw = 0

    while True:

        if not q_imu_out.empty():
            accel_data, gyro_data = await q_imu_out.get()

            ax = accel_data[0] / 4096
            ay = accel_data[1] / 4096
            az = accel_data[2] / 4096
            gx = gyro_data[0] / 65.5
            gy = gyro_data[1] / 65.5
            gz = gyro_data[2] / 65.5

            # Brokking
            # -----------------------------------------------------

            # dt = time.ticks_diff(time.ticks_us(), start_time) / 1000000
            # start_time = time.ticks_us()
            #
            # angle_roll_gyro += gx * dt
            # angle_pitch_gyro += gy * dt
            # angle_yaw_gyro += gz * dt
            #
            # yaw_effect = sin(gz * dt * 0.01745)
            # angle_roll_gyro += angle_pitch_gyro * yaw_effect
            # angle_pitch_gyro -= angle_roll_gyro * yaw_effect
            #
            # r = sqrt(ax ** 2 + ay ** 2 + az ** 2)
            #
            # angle_roll_acc = asin(ax / r) * 57.3  # to degrees
            # angle_pitch_acc = asin(ay / r) * 57.3  # to degrees
            #
            # angle_roll_gyro = angle_roll_gyro * 0.9996 + angle_roll_acc * 0.0004
            # angle_pitch_gyro = angle_pitch_gyro * 0.9996 + angle_pitch_acc * 0.0004
            #
            # roll = inertia * roll + (1.- inertia) * angle_roll_gyro
            # pitch = inertia * pitch + (1.-inertia) * angle_pitch_gyro
            # yaw = inertia * yaw + (1. - inertia) * angle_yaw_gyro
            #
            # await q_fusion_out.put_replace((roll, pitch, yaw))

            # Complementary Filter
            # -----------------------------------------------------
            # r = sqrt(ax ** 2 + ay ** 2 + az ** 2)
            #
            # accel_angle_x = asin(ax / r) * 57.3  # to degrees
            # accel_angle_y = asin(ay / r) * 57.3  # to degrees
            #
            # dt = time.ticks_diff(time.ticks_us(), start_time) / 1000000
            # start_time = time.ticks_us()
            #
            # roll = gyro_part * (roll + (gx * dt)) + accel_part * accel_angle_x
            # pitch = gyro_part * (pitch + (gy * dt)) + accel_part * accel_angle_y
            # yaw += gz * dt
            #
            # await q_fusion_out.put_replace((roll, pitch, yaw))

            # Madgwick Fusion
            # -----------------------------------------------------
            dt = time.ticks_diff(time.ticks_us(), start_time) / 1000000
            start_time = time.ticks_us()

            yaw += gz * dt

            gx = gx * 0.0174533
            gy = gy * 0.0174533
            gz = gz * 0.0174533

            q1 = q[0]
            q2 = q[1]
            q3 = q[2]
            q4 = q[3]

            # Auxiliary variables to avoid repeated arithmetic
            _2q1 = 2 * q1
            _2q2 = 2 * q2
            _2q3 = 2 * q3
            _2q4 = 2 * q4
            _4q1 = 4 * q1
            _4q2 = 4 * q2
            _4q3 = 4 * q3
            _8q2 = 8 * q2
            _8q3 = 8 * q3
            q1q1 = q1 * q1
            q2q2 = q2 * q2
            q3q3 = q3 * q3
            q4q4 = q4 * q4

            # Normalise accelerometer measurement
            norm = sqrt(ax * ax + ay * ay + az * az)
            norm = 1 / norm  # use reciprocal for division
            ax *= norm
            ay *= norm
            az *= norm

            # Gradient decent algorithm corrective step
            s1 = _4q1 * q3q3 + _2q3 * ax + _4q1 * q2q2 - _2q2 * ay
            s2 = _4q2 * q4q4 - _2q4 * ax + 4 * q1q1 * q2 - _2q1 * ay - _4q2 + _8q2 * q2q2 + _8q2 * q3q3 + _4q2 * az
            s3 = 4 * q1q1 * q3 + _2q1 * ax + _4q3 * q4q4 - _2q4 * ay - _4q3 + _8q3 * q2q2 + _8q3 * q3q3 + _4q3 * az
            s4 = 4 * q2q2 * q4 - _2q2 * ax + 4 * q3q3 * q4 - _2q3 * ay
            norm = 1 / sqrt(s1 * s1 + s2 * s2 + s3 * s3 + s4 * s4)  # normalise step magnitude
            s1 *= norm
            s2 *= norm
            s3 *= norm
            s4 *= norm

            # Compute rate of change of quaternion
            qDot1 = 0.5 * (-q2 * gx - q3 * gy - q4 * gz) - beta * s1
            qDot2 = 0.5 * (q1 * gx + q3 * gz - q4 * gy) - beta * s2
            qDot3 = 0.5 * (q1 * gy - q2 * gz + q4 * gx) - beta * s3
            qDot4 = 0.5 * (q1 * gz + q2 * gy - q3 * gx) - beta * s4

            q1 += qDot1 * dt
            q2 += qDot2 * dt
            q3 += qDot3 * dt
            q4 += qDot4 * dt
            norm = 1 / sqrt(q1 * q1 + q2 * q2 + q3 * q3 + q4 * q4)  # normalise quaternion
            q = q1 * norm, q2 * norm, q3 * norm, q4 * norm

            pitch = 57.3 * (-asin(2.0 * (q[1] * q[3] - q[0] * q[2])))
            roll = 57.3 * (atan2(2.0 * (q[0] * q[1] + q[2] * q[3]),
                                 q[0] * q[0] - q[1] * q[1] - q[2] * q[2] + q[3] * q[3]))

            await q_fusion_out.put_replace((-pitch, roll, yaw))

        await asyncio.sleep(asyncio_sleep_t)


async def base_task(q_fusion_out):
    global counter
    global lcd_text

    global ref_throttle
    global ref_roll
    global ref_pitch
    global ref_yaw

    global pos_latitude
    global pos_longitude
    global pos_altitude
    global pos_roll
    global pos_pitch
    global pos_yaw

    """
    for 50 Hz:
    T = 20 milli second : (1/50) * 1000
    
    min RPM at pulse width = 1 milli second, which is pulse width equal to 5% of period 
    max RPM at pulse width = 2 milli second, which is pulse width equal to 10% of period
    
    
    a full period is broken into (48 * 10^6 / freq) widthS.
    so the pulse with can vary between 0 and that number one by one.
    
    for 50 MHz, 0 <= pulse with <= 960,000
    and so a 5% and 10% pulse width refer to 48,000 and 96,000, respectively.


    """
    esc_min = 48000  # (5%) use when setting the PWM pin to avoid reconfiguration
    esc_max = 96000  # (10%) max value used in calibration
    esc_min_throttle = 49804  # (5.19%) minimum stable throttle such that blades rotate
    esc_max_throttle = 58594  # (6.1%) maximum safe throttle such that the engine won't smoke

    esc_min_pid_throttle = 49804  # minimum throttle while flying
    esc_max_pid_throttle = 58594  # maximum throttle while flying

    # PWM setup

    # pwm_pin_1 = Pin('C6', Pin.OUT)  # front right
    # pwm_pin_2 = Pin('C7', Pin.OUT)  # rear right
    # pwm_pin_3 = Pin('B8', Pin.OUT)  # rear left
    # pwm_pin_4 = Pin('B9', Pin.OUT)  # front left
    #
    # timer_3 = Timer(3, freq=50)  # for esc_1 and esc_2
    # timer_4 = Timer(4, freq=50)  # for est_3 and esc_4
    #
    # esc_1 = timer_3.channel(1, Timer.PWM, pin=pwm_pin_1, pulse_width=esc_min)
    # esc_2 = timer_3.channel(2, Timer.PWM, pin=pwm_pin_2, pulse_width=esc_min)
    # esc_3 = timer_4.channel(3, Timer.PWM, pin=pwm_pin_3, pulse_width=esc_min)
    # esc_4 = timer_4.channel(4, Timer.PWM, pin=pwm_pin_4, pulse_width=esc_min)

    # for LED
    esc_min_pid_throttle = 0
    esc_max_pid_throttle = 960000

    # two leds
    # pwm_pin_1 = Pin('B4', Pin.OUT)  # blue
    # pwm_pin_2 = Pin('A15', Pin.OUT)  # yellow
    # pwm_pin_3 = Pin('B4', Pin.OUT)  # green
    # pwm_pin_4 = Pin('A15', Pin.OUT)  # blue
    #
    # timer_2 = Timer(2, freq=1000)
    # timer_3 = Timer(3, freq=1000)
    # esc_1 = timer_3.channel(1, Timer.PWM, pin=pwm_pin_1, pulse_width=esc_min)
    # esc_2 = timer_2.channel(1, Timer.PWM, pin=pwm_pin_2, pulse_width=esc_min)
    # esc_3 = timer_3.channel(1, Timer.PWM, pin=pwm_pin_3, pulse_width=esc_min)
    # esc_4 = timer_2.channel(1, Timer.PWM, pin=pwm_pin_4, pulse_width=esc_min)


    # one leds
    pwm_pin_1 = Pin('B4', Pin.OUT)  # blue

    timer_3 = Timer(3, freq=1000)
    esc_1 = timer_3.channel(1, Timer.PWM, pin=pwm_pin_1, pulse_width=esc_min)
    esc_2 = timer_3.channel(1, Timer.PWM, pin=pwm_pin_1, pulse_width=esc_min)
    esc_3 = timer_3.channel(1, Timer.PWM, pin=pwm_pin_1, pulse_width=esc_min)
    esc_4 = timer_3.channel(1, Timer.PWM, pin=pwm_pin_1, pulse_width=esc_min)



    # print('connect battery')
    # await asyncio.sleep(5)
    # print('go..')

    esc_1_v = copy.deepcopy(esc_min_throttle)
    esc_2_v = copy.deepcopy(esc_min_throttle)
    esc_3_v = copy.deepcopy(esc_min_throttle)
    esc_4_v = copy.deepcopy(esc_min_throttle)

    esc_1.pulse_width(esc_1_v)
    esc_2.pulse_width(esc_2_v)
    esc_3.pulse_width(esc_3_v)
    esc_4.pulse_width(esc_4_v)

    # params
    k_p_roll = 100000  # as far you are to the target, the bigger the force
    k_i_roll = 0  # it's taking too long, the longer it takes the higher the cost.
    k_d_roll = 0  # you are going way too fast. slow down.
    min_roll_i = 5.0
    max_i_to_p_roll = 0.10
    pid_max_roll = 1500000 # int(0.1 * (esc_max_pid_throttle - esc_min_pid_throttle))

    k_p_pitch = k_p_roll
    k_i_pitch = k_i_roll
    k_d_pitch = k_d_roll
    min_pitch_i = min_roll_i
    max_i_to_p_pitch = max_i_to_p_roll
    pid_max_pitch = pid_max_roll

    k_p_yaw = k_p_roll / 100
    k_i_yaw = 0.02
    k_d_yaw = 0.0
    min_yaw_i = min_roll_i
    max_i_to_p_yaw = max_i_to_p_roll
    pid_max_yaw = pid_max_roll

    pid_roll = PID(name='roll',
                   k_p=k_p_roll,
                   k_i=k_i_roll,
                   k_d=k_d_roll,
                   min_angle_i=min_roll_i,
                   max_i_to_p=max_i_to_p_roll,
                   pid_max=pid_max_roll)

    pid_pitch = PID(name='pitch',
                    k_p=k_p_pitch,
                    k_i=k_i_pitch,
                    k_d=k_d_pitch,
                    min_angle_i=min_pitch_i,
                    max_i_to_p=max_i_to_p_pitch,
                    pid_max=pid_max_pitch)

    pid_yaw = PID(name='yaw',
                  k_p=k_p_yaw,
                  k_i=k_i_yaw,
                  k_d=k_d_yaw,
                  min_angle_i=min_yaw_i,
                  max_i_to_p=max_i_to_p_yaw,
                  pid_max=pid_max_yaw)
    freq = 120
    period = 1. / freq

    # log file
    write_log = False
    f = open('data.csv', 'w')
    f.write(
        'total_time,delta_time,roll_angle,pid_roll,pid_roll.p,pid_roll.i,pid_roll.d,esc_1_v,esc_2_v,esc_3_v,esc_4_v\n')

    total_time = 0

    # start the timing only when the first fusion is prepared
    while q_fusion_out.empty():
        await asyncio.sleep(asyncio_sleep_t)

    start_time = time.ticks_us()

    time_len = const(500)
    while time.ticks_diff(time.ticks_ms(), root_start_time) / 1000 < time_len:

    #while True:

        if not q_fusion_out.empty():
            # new fusion data has arrived
            # perform actions
            roll_angle, pitch_angle, yaw_angle = await q_fusion_out.get()
            lcd_text = f'{round(roll_angle, 2)}, {round(pitch_angle, 2)}\n {round(yaw_angle, 2)}'

            # update global pos variables
            pos_roll = roll_angle
            pos_pitch = pitch_angle
            pos_yaw = yaw_angle

            # implement ref values from either the joystick or flight computer
            throttle = int(esc_min_pid_throttle + (ref_throttle / 100) * (esc_max_pid_throttle - esc_min_pid_throttle))
            target_roll = 10 * (ref_roll / 100)
            target_pitch = 10 * (ref_pitch / 100)
            target_yaw = 180 * (ref_yaw / 100)
            roll_angle = roll_angle - target_roll
            pitch_angle = pitch_angle - target_pitch
            yaw_angle = yaw_angle - target_yaw

            # Regulate the frequency to a fixed value.
            # this is because PID multipliers are calibrated for a certain freq only.
            # No asyincio here. Goal is to regulate a fixed freq. Also, you can't yield before issuing PWM.
            while time.ticks_diff(time.ticks_us(), start_time) / 1000000 < period:
                time.sleep_us(1)

            dt = time.ticks_diff(time.ticks_us(), start_time) / 1000000
            start_time = time.ticks_us()
            # lcd_text = f'{dt}'
            # print(f'{dt}')

            # PID UPDATE
            pid_roll.update(roll_angle, dt)
            pid_pitch.update(pitch_angle, dt)
            pid_yaw.update(yaw_angle, dt)

            # APPLY
            esc_1_v = throttle + pid_roll.pid + pid_pitch.pid - pid_yaw.pid
            esc_2_v = throttle + pid_roll.pid - pid_pitch.pid + pid_yaw.pid
            esc_3_v = throttle - pid_roll.pid - pid_pitch.pid - pid_yaw.pid
            esc_4_v = throttle - pid_roll.pid + pid_pitch.pid + pid_yaw.pid

            esc_1_v = min(max(esc_1_v, esc_min_pid_throttle), esc_max_pid_throttle)
            esc_2_v = min(max(esc_2_v, esc_min_pid_throttle), esc_max_pid_throttle)
            esc_3_v = min(max(esc_3_v, esc_min_pid_throttle), esc_max_pid_throttle)
            esc_4_v = min(max(esc_4_v, esc_min_pid_throttle), esc_max_pid_throttle)

            esc_1.pulse_width(int(esc_1_v))
            esc_2.pulse_width(int(esc_2_v))
            esc_3.pulse_width(int(esc_3_v))
            esc_4.pulse_width(int(esc_4_v))

            # esc_1.pulse_width_percent(int(map_range(pitch_angle, -45, 45, 0, 50)))
            # esc_2.pulse_width_percent(int(map_range(roll_angle, -45, 45, 0, 50)))
            # esc_3.pulse_width_percent(int(map_range(pitch_angle, -45, 45, 0, 50)))
            # esc_4.pulse_width_percent(int(map_range(roll_angle, -45, 45, 0, 50)))

            # esc_1.pulse_width(int(map_range(nrf_out[0], 0, 100, 0, 960000)))
            # esc_2.pulse_width(int(map_range(nrf_out[1], 0, 100, 0, 960000)))
            # esc_3.pulse_width(int(map_range(nrf_out[2], 0, 100, 0, 960000)))
            # esc_4.pulse_width_percent(int(map_range(roll_angle, -45, 45, 0, 50)))

            counter = counter + 1

            if write_log:
                total_time += dt
                f.write(
                    f'{total_time}, {dt}, {roll_angle}, {pid_roll.pid}, {pid_roll.p},{pid_roll.i},{pid_roll.d}, {esc_1_v}, {esc_2_v}, {esc_3_v}, {esc_4_v}\n')

        # yield to the scheduler
        await asyncio.sleep(asyncio_sleep_t)

    f.close()

async def main():
    q_imu_out = queue.Queue(maxsize=1)
    q_fusion_out = queue.Queue(maxsize=1)

    task_1 = asyncio.create_task(sensor_sample(q_imu_out))
    task_2 = asyncio.create_task(fusion(q_imu_out, q_fusion_out))
    task_3 = asyncio.create_task(base_task(q_fusion_out))
    task_4 = asyncio.create_task(nrf_non_autonomous())
    # task_5 = asyncio.create_task(lcd_write())


    await task_3

    print('freq: ', counter / time_len)
    print('T: ', time_len / counter)



# root_start_time = time.ticks_ms()
# counter = 0
# time_len = 10
# while time.ticks_diff(time.ticks_ms(), root_start_time) / 1000 < time_len:
# #
#     a = imu.accel.xyz
#     b = imu.gyro.xyz
#     fuse.update_nomag(imu.accel.xyz, imu.gyro.xyz)
# #
# #
# #
#     # timer_2_channel_1.pulse_width_percent(int(map_range(fuse.roll, -1, 1, 0, 100)))
#     # timer_2_channel_2.pulse_width_percent(int(map_range(fuse.pitch, -1, 1, 0, 100)))
#     counter = counter + 1
# #
# print('freq: ', counter / time_len)
# print('T: ',time_len / counter)


asyncio.run((main()))
