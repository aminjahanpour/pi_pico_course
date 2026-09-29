from machine import Pin, ADC, PWM
import time

pot_pin = ADC(Pin(26))
pwm_pin = PWM(Pin(15))

pwm_pin.freq(1000)

while True:
    pot_value = pot_pin.read_u16()

    duty_cycle = pot_value

    pwm_pin.duty_u16(duty_cycle)

    print(duty_cycle)
    time.sleep(0.01)

    

