from machine import Pin, ADC, PWM
import time

# Passive buzzer
# the passibe buzzer is the one with equal pins
# we drive it with a PWM pin b changing the frequency.
# the duty cycle is meant to stay at 50% to produce the max volume

pot_pin = ADC(Pin(26))
pwm_pin = PWM(Pin(16))

pwm_pin.duty_u16(32768)  # 50% duty cycle = max volume

while True:
    pot_value = pot_pin.read_u16()
    # Map 0-65535 → 200-4000 Hz
    freq = 200 + (pot_value * 3800) // 65535
    pwm_pin.freq(freq)
    print(freq)
    time.sleep(0.01)   