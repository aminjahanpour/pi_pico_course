from time import sleep
from machine import Pin, ADC
import utime

from ulora import LoRa, ModemConfig, SPIConfig





board_led = Pin(25, Pin.OUT)
board_led(1)
utime.sleep(0.3)
board_led(0)

sensor_temp = ADC(4)

# Lora Parameters
spi_bus = SPIConfig.pico_0

# pico config
reset_pin = 20
cs_pin = 17
interrupt_pin = 21


transmit_power_dbm = 23
server_address = 1

client_address = 21, #69

# initialise radio
lora = LoRa(spi_channel=spi_bus,
            interrupt=interrupt_pin,
            this_address=client_address,
            cs_pin=cs_pin,
            reset_pin=reset_pin,
            tx_power=transmit_power_dbm,
            acks=True)



########
# RECEIVER

# This is our callback function that runs when a message is received
# def on_recv(payload):
#     print(payload)
#
# # set callback
# lora.on_recv = on_recv
#
# # set to listen continuously
# lora.set_mode_rx()
#
# while True:
#     sleep(0.01)


########
# SENDER

while True:
    temperature = sensor_temp.read_u16() * (3.3/65535)
    temperature = 27 - (temperature - 0.706)/0.001721
    print(temperature)
    lora.send_to_wait(data=str(temperature),
                      header_to=server_address
                      )
    board_led.toggle()
    # print("sent")
    utime.sleep(0.1)
