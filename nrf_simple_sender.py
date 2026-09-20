from machine import SoftI2C, SoftSPI, Pin, I2C
from nrf24l01 import NRF24L01
import struct
import time

white_led = Pin('A14')
white_led.low()
yellow_led = Pin('A15')
white_led.low()

pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")

cs = Pin("C4", mode=Pin.OUT, value=1)
ce = Pin("C5", mode=Pin.OUT, value=0)
spi = SoftSPI(sck="A5", mosi="A7", miso="A6")
nrf = NRF24L01(spi, cs, ce, payload_size=12)

nrf.open_tx_pipe(pipes[1])
nrf.open_rx_pipe(1, pipes[0])

nrf.start_listening()



while True:

    white_led.high()
    nrf.stop_listening()

    try:
        nrf.send(struct.pack("iii", 1, 2, 3))
    except OSError:
        pass
    nrf.start_listening()

    white_led.low()

    time.sleep(0.5)
