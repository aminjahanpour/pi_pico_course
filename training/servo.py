import machine
import utime
from machine import Pin

potentiometer = machine.ADC(28)

servo = machine.PWM(Pin(2))
servo.freq(50)

def interval_mapping(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def angle_to_duty(pin, angle):
    # map the angle range 0 ~ 180 to the pulse width range 0.5 ~ 2.5ms
    pulse_width = interval_mapping(angle, 0, 180, 0.5, 2.5)

    # convert the pulse width from period to duty
    duty = int(interval_mapping(pulse_width, 0, 20, 0, 65535))

    return duty



while True:
    current_duty = servo.duty_u16()

    target_angle = interval_mapping(potentiometer.read_u16(), 0, pow(2, 16), 0, 180)
    target_duty = angle_to_duty(servo, target_angle)

    print(f'current_duty: {current_duty} to -> {target_duty}')

    if abs(target_duty - current_duty) > 200:
        print('rotating...')
        servo.duty_u16(target_duty)
        print('done')

    utime.sleep(0.5)
