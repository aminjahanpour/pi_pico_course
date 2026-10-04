from machine import Pin, ADC, PWM
import time

pot_pin = ADC(Pin(26))
pwm_pin = PWM(Pin(15))

# while controlling an LED light, a frequency of 1000 Hz is generally used
pwm_pin.freq(1000)

while True:
    
    # reading a 16-bit integer from ADC
    pot_value = pot_pin.read_u16()

    duty_cycle = pot_value

    # writing a 16-bit integer as Duty Cycle on my PWM
    pwm_pin.duty_u16(duty_cycle)

    print(duty_cycle)
    time.sleep(0.01)

    

