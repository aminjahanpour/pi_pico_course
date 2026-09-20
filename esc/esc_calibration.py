from utime import sleep
from machine import Pin, I2C, PWM, ADC
import time


def map_range(v, input_min, input_max, output_min, output_max):
    return output_min + ((v - input_min) / (input_max - input_min)) * (output_max - output_min)


pwm_pins = [17,18,19,20]

esc_modules = []

for pwm_pin in pwm_pins:
    esc_module = PWM(Pin(pwm_pin))
    esc_module.freq(50)

    esc_modules.append(esc_module)

print(esc_modules)


print("connect the battery")
sleep(10)

v_max = 0.1 #  6553
v_min = 0.05 # 3276


print('v_max')
v = v_max
for esc_module in esc_modules:
    esc_module.duty_u16(int(v * pow(2, 16)))
sleep(5)


print('v_min')
v = v_min
for esc_module in esc_modules:
    esc_module.duty_u16(int(v * pow(2, 16)))
sleep(6)


print('v_mean')
v = 3400
for esc_module in esc_modules:
    esc_module.duty_u16(v)
sleep(10)
