from machine import Pin, SPI
from nrf24l01 import NRF24L01
import struct
import time


# ==============================
# NRF24L01
# ==============================

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

radio.open_rx_pipe(0, b"NODE2")
radio.start_listening()


print()
print("==============================")
print("JOYSTICK RECEIVER READY")
print("==============================")

print("CONFIG    :", hex(radio.reg_read(0x00)))
print("EN_RXADDR :", hex(radio.reg_read(0x02)))
print("RF_CH     :", hex(radio.reg_read(0x05)))
print("RF_SETUP  :", hex(radio.reg_read(0x06)))

print()


# ==============================
# MAIN LOOP
# ==============================

while True:

    if radio.any():

        data = radio.recv()

        # Unpack:
        #   2 bytes X
        #   2 bytes Y
        #   1 byte button
        x, y, sw = struct.unpack("<HHB", data[:5])

        print(
            "X:", x,
            "Y:", y,
            "SW:", sw
        )

    time.sleep_ms(10)
