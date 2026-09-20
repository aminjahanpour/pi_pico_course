import utime
from utime import sleep
from machine import Pin, I2C, PWM, SPI
# from lcd1602 import LCD
from lib import copy
from nrf24l01 import NRF24L01
import struct
from imu import MPU6050
from fusion import Fusion
from math import tan

# Slave pause between receiving data and checking for further packets.
_RX_POLL_DELAY = const(15)
# Slave pauses an additional _SLAVE_SEND_DELAY ms after receiving data and before
# transmitting to allow the (remote) master time to get into receive mode. The
# master may be a slow device. Value tested with Pyboard, ESP32 and ESP8266.
_SLAVE_SEND_DELAY = const(10)

nrf_cfg = {"spi": 0, "miso": 4, "mosi": 7, "sck": 6, "csn": 15, "ce": 14}

# Addresses are in little-endian format. They correspond to big-endian
# 0xf0f0f0f0e1, 0xf0f0f0f0d2
pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")

def map_range(v, input_min, input_max, output_min, output_max):
    return output_min + ((v - input_min) / (input_max - input_min)) * (output_max - output_min)

def angle_to_duty(angle):
    # map the angle range 0 ~ 180 to the pulse width range 0.5 ~ 2.5ms
    pulse_width = map_range(angle, 0, 180, 0.5, 2.5)

    # convert the pulse width from period to duty
    duty = int(map_range(pulse_width, 0, 20, 0, 65535))

    return duty

def center_servos():
    # all 3 servos reset to 90 degrees
    servo_north.duty_u16(angle_to_duty(90))
    servo_left.duty_u16(angle_to_duty(90))
    servo_right.duty_u16(angle_to_duty(90))


# lcd = LCD(I2C(0, sda=Pin(0), scl=Pin(1), freq=400000))

imu = MPU6050(I2C(1, sda=Pin(2), scl=Pin(3), freq=400000))
fuse = Fusion()


esc_main = PWM(Pin(16))
esc_tail = PWM(Pin(17))

servo_north = PWM(Pin(19))
servo_left = PWM(Pin(20))
servo_right = PWM(Pin(18))


esc_main.freq(50)
esc_tail.freq(50)

servo_north.freq(50)
servo_left.freq(50)
servo_right.freq(50)


v_max = int(0.1 * pow(2, 16)) # 6554
v_min = int(0.05 * pow(2, 16)) # 3277
v_initiate = int(0.07 * pow(2, 16)) # 3932

esc_tail.duty_u16(int(v_min))
esc_main.duty_u16(int(v_min))


# NRF
csn = Pin(nrf_cfg["csn"], mode=Pin.OUT, value=1)
ce = Pin(nrf_cfg["ce"], mode=Pin.OUT, value=0)
if nrf_cfg["spi"] == -1:
    spi = SPI(-1, sck=Pin(nrf_cfg["sck"]), mosi=Pin(nrf_cfg["mosi"]), miso=Pin(nrf_cfg["miso"]))
    nrf = NRF24L01(spi, csn, ce, payload_size=8)
else:
    nrf = NRF24L01(SPI(nrf_cfg["spi"]), csn, ce, payload_size=12)

nrf.open_tx_pipe(pipes[1])
nrf.open_rx_pipe(1, pipes[0])
nrf.start_listening()



#reset servos
center_servos()


# lcd.message(f"power on")
sleep(5)
# lcd.clear()

print('here')


value_left = 3200
value_right = 3200


current_duty_north = servo_north.duty_u16()
print('initial duty', current_duty_north)

esc_min = 3200
esc_max = 4000

min_servo_duty = 4200 # z = 0
max_servo_duty = 5525 # z = 6.3
z_min = 0
z_max = 6.3
cp = 0.5 * (z_min + z_max) # duty = 4862

def disk_z(pitch_deg, roll_deg, cp):
    z_north = 40 * tan(pitch_deg) + cp
    z_left = -28.28 * (tan(pitch_deg) - tan(roll_deg)) + cp
    z_right = -28.28 * (tan(pitch_deg) + tan(roll_deg)) + cp
    return z_north, z_left, z_right

def flip_z(z):
    if z < cp:
        z = cp + (cp - z)
    elif z > cp:
        z = cp - (z - cp)
    return z

def z_to_duty(target_z):
    """
    increasing the duty, lowers the arm
    """
    return int(max_servo_duty - ((target_z-z_min)/(z_max-z_min)) * (max_servo_duty-min_servo_duty))

# counter  = 0
print(z_to_duty(cp))
while True:


    if nrf.any():
        while nrf.any():

            buf = nrf.recv()
            v_1, v_2, v_3 = struct.unpack("iii", buf)

            # print(v_1, v_2, v_3)

            value_esc_main = copy.deepcopy(v_1)
            value_esc_tail = copy.deepcopy(v_2)
            value_cp = copy.deepcopy(v_3)

            esc_main.duty_u16(int(map_range(value_esc_main, 0, 99, esc_min, esc_max)))
            esc_tail.duty_u16(int(map_range(value_esc_tail, 0, 99, esc_min, esc_max)))
            cp = map_range(value_cp, 0, 99, z_min, z_max)

            # lcd.clear()
            # #
            # lcd.message(f"{value_servo_north}, {value_servo_left}, {value_servo_right}")

            utime.sleep_ms(_RX_POLL_DELAY)
            # Give master time to get into receive mode.
            utime.sleep_ms(_SLAVE_SEND_DELAY)

            nrf.start_listening()


    fuse.update_nomag(imu.accel.xyz, imu.gyro.xyz)
      
    fuse_pitch = fuse.pitch
    fuse_roll = fuse.roll

    #print(disk_z(-fuse_pitch*3.1415/180, fuse_roll*3.1415/180, cp=0))
    
    z_north, z_left, z_right = disk_z(-fuse_pitch*3.1415/180, fuse_roll*3.1415/180, cp)

    re_duty_north = z_to_duty(flip_z(z_north))
    re_duty_north = max(min(re_duty_north, max_servo_duty), min_servo_duty)

    re_duty_left = z_to_duty(flip_z(z_left))
    re_duty_left = max(min(re_duty_left, max_servo_duty), min_servo_duty)

    re_duty_right = z_to_duty(flip_z(z_right))
    re_duty_right = max(min(re_duty_right, max_servo_duty), min_servo_duty)

    #if counter % 200 ==  0 :
    #    print(z_north, flip_z(z_north), z_to_duty(flip_z(z_north)))
    
    servo_north.duty_u16(re_duty_north)
    servo_left.duty_u16(re_duty_left)
    servo_right.duty_u16(re_duty_right)


    # counter += 1


