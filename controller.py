from machine import Pin, ADC, SPI
import struct
from nrf24l01 import NRF24L01
from lib import toolkit

# Slave pause between receiving data and checking for further packets.
_RX_POLL_DELAY = const(15)
# Slave pauses an additional _SLAVE_SEND_DELAY ms after receiving data and before
# transmitting to allow the (remote) master time to get into receive mode. The
# master may be a slow device. Value tested with Pyboard, ESP32 and ESP8266.
_SLAVE_SEND_DELAY = const(10)

cfg = {"spi": 0, "miso": 4, "mosi": 7, "sck": 6, "csn": 15, "ce": 14}
# Addresses are in little-endian format. They correspond to big-endian
# 0xf0f0f0f0e1, 0xf0f0f0f0d2
pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")

csn = Pin(cfg["csn"], mode=Pin.OUT, value=1)
ce = Pin(cfg["ce"], mode=Pin.OUT, value=0)
if cfg["spi"] == -1:
    spi = SPI(-1, sck=Pin(cfg["sck"]), mosi=Pin(cfg["mosi"]), miso=Pin(cfg["miso"]))
    nrf = NRF24L01(spi, csn, ce, payload_size=8)
else:
    nrf = NRF24L01(SPI(cfg["spi"]), csn, ce, payload_size=12)

nrf.open_tx_pipe(pipes[0])
nrf.open_rx_pipe(1, pipes[1])
nrf.start_listening()

toolkit.pico_led_blink()

pt_1 = ADC(26)
pt_2 = ADC(27)
pt_3 = ADC(28)

denominator = pow(2, 16)

toolkit.pico_led_blink()

while True:
    nrf.stop_listening()

    v_1 = int(pt_1.read_u16() / denominator * 100)
    v_2 = int(pt_2.read_u16() / denominator * 100)
    # v_3 = int(pt_3.read_u16() / denominator * 100)

    v_3 = int((denominator - pt_3.read_u16()) / denominator * 100)

    # print(v_1, v_2, v_3)

    try:
        nrf.send(struct.pack("iii", v_1, v_2, v_3))
    except OSError:
        pass

    nrf.start_listening()

    # v = f"{v_1},{v_2},{v_3}"
    # print(v)
    # lora.send(data=v, header_to=asset_id)

    # try:
    #     # nrf.send(struct.pack("iii", v_1, v_2, v_3))
    #     print(v_1)
    #     nrf.send(struct.pack("i", v_1))
    #
    #     nrf.send("\n")
    #     # toolkit.pico_led_blink()
    # except:
    #     pass
    #     print('err')

    # time.sleep(0.8)

