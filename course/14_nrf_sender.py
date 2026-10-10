
from machine import Pin, SPI, ADC
from nrf24l01 import NRF24L01
import struct
import time

led = Pin(25, Pin.OUT)

# JOYSTICK
x_axis = ADC(Pin(26))
y_axis = ADC(Pin(27))
button = Pin(15, Pin.IN, Pin.PULL_UP)

# NRF24L01
spi = SPI(
    0,
    baudrate=1_000_000,
    polarity=0,
    phase=0,
    sck=Pin(18),
    mosi=Pin(19),
    miso=Pin(16)
)

csn = Pin(20, Pin.OUT, value=1)
ce = Pin(17, Pin.OUT, value=0)

radio = NRF24L01(
    spi,
    csn,
    ce,
    channel=46,
    payload_size=8
)

radio.open_tx_pipe(b"NODE2")
radio.stop_listening()

print("TRANSMITTER READY")
print("CONFIG:", hex(radio.reg_read(0x00)))
print("RF_CH:", hex(radio.reg_read(0x05)))
print("RF_SETUP:", hex(radio.reg_read(0x06)))

counter_ = 0

while True:

    counter_ += 1

    if counter_ >= 2:
        led.toggle()
        counter_ = 0

    # Read joystick
    x = x_axis.read_u16()
    y = y_axis.read_u16()
    sw = button.value()

    # Transmit X, Y, and SW only
    # 2 bytes + 2 bytes + 1 byte + 3 padding bytes = 8 bytes
    message = struct.pack("<HHBxxx", x, y, sw)

    attempts = 0

    while True:
        attempts += 1

        try:
            radio.send(message)

            print(
                "SUCCESS:",
                "X:", x,
                "Y:", y,
                "SW:", sw,
                "attempts:", attempts
            )
            break

        except OSError as e:
            print(
                "RETRY:",
                "attempt:", attempts,
                "error:", e
            )
            time.sleep_ms(20)

    time.sleep_ms(100)

