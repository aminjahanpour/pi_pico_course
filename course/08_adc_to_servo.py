from machine import Pin, ADC, PWM
import time

# this is our go-to pin for analog sinals
pot_pin = ADC(Pin(26))

# let's have the servo on the top left pin (GPIO0)
# remember to power servo from VBUS (+5v)
servo = PWM(Pin(0))

# 50 Hz is the frequency we use for this servie
servo.freq(50)



while True:
    
    # read the 16-bit integer from ADC
    pot_value = pot_pin.read_u16()

    # Now we need to map that 16-bit integer to servo position
    # we do a linear mapping from 3277 (for 0 degrees) to 6554 (for 180 degrees)
    duty_cycle = int(3277 + (pot_value / 65535) * (6554 - 3277))

    servo.duty_u16(duty_cycle)

    print(pot_value, duty_cycle)
    time.sleep(0.02)
