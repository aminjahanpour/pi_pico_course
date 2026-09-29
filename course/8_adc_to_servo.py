from machine import Pin, ADC, PWM
import time

pot_pin = ADC(Pin(26))
servo = PWM(Pin(15))

servo.freq(50)

while True:
    pot_value = pot_pin.read_u16()

    # Map potentiometer to servo position
    duty_cycle = int(3277 + (pot_value / 65535) * (6554 - 3277))

    servo.duty_u16(duty_cycle)

    print(pot_value, duty_cycle)
    time.sleep(0.02)
