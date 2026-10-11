from machine import Pin, PWM
import time

pwm_pin = PWM(Pin(15))

# Set PWM frequency to 1000 Hz
pwm_pin.freq(1000)

while True:

    # Dance 1: Slowly fade in
    for duty in range(0, 65536, 1000):
        pwm_pin.duty_u16(duty)
        time.sleep(0.01)

    # Dance 2: Slowly fade out
    for duty in range(65535, -1, -1000):
        pwm_pin.duty_u16(duty)
        time.sleep(0.01)

    # Dance 3: Quick flashes
    for i in range(5):
        pwm_pin.duty_u16(65535)  # Full brightness
        time.sleep(0.1)

        pwm_pin.duty_u16(0)      # LED off
        time.sleep(0.1)

    # Dance 4: Take a little break
    time.sleep(0.5)