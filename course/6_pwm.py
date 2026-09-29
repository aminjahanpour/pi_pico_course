from machine import Pin, PWM


# any GPIO pin can also be a PWM pin
pwm_pin = PWM(Pin(15))

# frequency: how many times in a second the pin is turned on and off
# this works fine for an LED
pwm_pin.freq(1000)


max_duty_cycle = 65535

# duty cycle: what percentage of the time, the pin is on
duty_cycle = int(0.95 * max_duty_cycle)


pwm_pin.duty_u16(duty_cycle)