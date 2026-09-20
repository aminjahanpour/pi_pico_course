from machine import SoftI2C, SoftSPI, Pin, I2C
from nrf24l01 import *
import struct
import utime

white_led = Pin('A14')
white_led.low()
yellow_led = Pin('A15')
white_led.low()

pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")

# pipes = (b"\x0B\x16\x21\x2C\x37", b"\x42\x4D\x58\x63\x6E")
# pipes = (b"\x37\x2C\x21\x16\x0B", b"\x6E\x63\x58\x4D\x42")

cs = Pin("C4", mode=Pin.OUT, value=1)
ce = Pin("C5", mode=Pin.OUT, value=0)
spi = SoftSPI(sck="A5", mosi="A7", miso="A6")
nrf = NRF24L01(spi, cs, ce, channel=64, payload_size=32, power=POWER_0, speed=SPEED_2M)

nrf.open_tx_pipe(pipes[1])
nrf.open_rx_pipe(1, pipes[0])

nrf.start_listening()

white_led.low()

while True:
    if nrf.any():
        while nrf.any():
            white_led.high()

            buf = nrf.recv()
            if (buf[0]==70 and buf[1] == 114):
                # print(buf)
                total_bytes = ((buf[5] & 0xff) << 16) | ((buf[6] & 0xff) << 8) | (buf[7] & 0xff)
                crc32_value_from_greeting = ((buf[10] & 0xff) << 24) | ((buf[11] & 0xff) << 16) | ((buf[12] & 0xff) << 8) | (buf[13] & 0xff)
                crc32_value_calculated = ((buf[14] & 0xff) << 24) | ((buf[15] & 0xff) << 16) | ((buf[16] & 0xff) << 8) | (buf[17] & 0xff)
                print(f'total bytes: {total_bytes}, crc32_value_from_greeting: {crc32_value_from_greeting}, crc32_value_calculated: {crc32_value_calculated}')
                if (crc32_value_from_greeting !=crc32_value_calculated):
                    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')


            # v_1, v_2, v_3 = struct.unpack("iii", buf)

            # print(v_1, v_2, v_3)

            nrf.start_listening()
        white_led.low()


