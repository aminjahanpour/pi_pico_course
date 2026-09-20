import machine
import utime
import urandom
from machine import Pin
from lib.lcd1602 import LCD
import _thread

lcd = LCD()
lcd.clear()

led_yellow = Pin(13, Pin.OUT)
led_yellow.off()

red_led = machine.PWM(Pin(15))
red_led.freq(1000)
red_led.duty_u16(0)

button = Pin(14, Pin.IN, Pin.PULL_UP)

buzzer = machine.PWM(Pin(16))

potentiometer = machine.ADC(28)

# greeting
board_led = Pin(25, Pin.OUT)
board_led(1)
utime.sleep(3)
board_led(0)

global responded
global timer_start
responded = False

score = 0




def display_thread(message):
    lcd.message(str(message))
    utime.sleep(2)
    lcd.clear()


def led_yellow_thread():
    while True:
        led_yellow.toggle()
        utime.sleep(2)


def tone(pin, frequency, duration):
    pin.freq(frequency)
    pin.duty_u16(30000)
    utime.sleep_ms(duration)
    pin.duty_u16(0)


def button_press(pin):
    global responded
    global score
    print('button press')
    button.irq(handler=None)

    if red_led.duty_u16() > 100:

        reaction_time = utime.ticks_diff(utime.ticks_ms(), timer_start)
        score = score + 5000 - reaction_time

        message = f're time: {str(reaction_time)} \nscore = {str(score)}'

        _thread.start_new_thread(display_thread, ([message]))

        tone(buzzer, 440, 250)

        red_led.duty_u16(0)
    else:
        score = score - 1000
        message = f'led was off\nscore = {str(score)}'

        _thread.start_new_thread(display_thread, ([message]))

        tone(buzzer, 494, 250)

    responded = True
    button.irq(trigger=machine.Pin.IRQ_RISING, handler=button_press)


def main():
    global responded
    global timer_start

    button.irq(trigger=machine.Pin.IRQ_RISING, handler=button_press)

    while True:

        red_led.duty_u16(0)

        utime.sleep(urandom.uniform(2, 4))
        red_led.duty_u16(int(potentiometer.read_u16() / 10))

        timer_start = utime.ticks_ms()

        responded = False

        while True:
            utime.sleep(0.01)
            red_led.duty_u16(int(red_led.duty_u16() / 1.01))

            if utime.ticks_diff(utime.ticks_ms(), timer_start) > 5000:
                if not responded:
                    message = 'missed this one'

                    _thread.start_new_thread(display_thread, ([message]))
                    tone(buzzer, 523, 250)

                break


if __name__ == '__main__':
    main()
