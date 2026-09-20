import utime
from machine import UART
from machine import Pin

led = Pin(13, Pin.OUT)
led.on()
utime.sleep(1)
led.off()


lora = UART(1,
            baudrate=9600,
            bits=8,
            parity=None,
            stop=1,
            tx=10,
            rx=9,
            rts=-1,
            cts=-1,
            txbuf=256,
            rxbuf=256,
            timeout=0,
            timeout_char=2)

while 1:
    if not lora.readline() is None:
        led.on()
        break
    utime.sleep(0.1)

while True:
    utime.sleep(10)
