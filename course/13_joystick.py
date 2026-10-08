from machine import Pin, ADC
import time


x = ADC(Pin(26))
y = ADC(Pin(27))
sw = Pin(15, Pin.IN, Pin.PULL_UP)

while True:
    x_ = x.read_u16() / 32768
    y_ = y.read_u16() / 32768

    print(x_ , y_ , sw.value())
    time.sleep(0.05)
