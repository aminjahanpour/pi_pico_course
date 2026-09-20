from machine import Pin, I2C, PWM
# from AS726X import AS726X
from ulora import LoRa
import time

# greetings

this_address = 0

spi_bus = (0, 18, 19, 16)

reset_pin = 20
cs_pin = 17
interrupt_pin = 21


lora = LoRa(

            spi_channel=spi_bus,
            interrupt=interrupt_pin,

            this_address=this_address,

            cs_pin=cs_pin,
            reset_pin=reset_pin,

            freq=902.0,

            tx_power=23,

            receive_all=True,
            )



def on_recv(payload):

    print(payload)

    message = payload.message.decode()
    print(message)

    # if message == 'status':
    #     lora.send(data='online', header_to=1)
    #     print('sent status=online to Station')
    #
    # elif message == 'read':
    #     sensor_values = read()
    #
    #     time.sleep(0.1)
    #
    #     print(sensor_values)
    #
    #     lora.send(data=f'read,{sensor_values}', header_to=1)
    #
    #     print('sent sensor_values to Station')
    #
    # else:
    #     dvs = [float(x) for x in message.split(',')]
    #
    #     outcome = perform_dvs(dvs)
    #
    #     time.sleep(0.1)
    #
    #     outcome = 'complete' if outcome else 'failed'
    #
    #     print(outcome)
    #
    #     lora.send(data=f'action_done,{outcome}', header_to=1)
    #
    #     print('sent outcome to Station')

    lora.set_mode_rx()



lora.on_recv = on_recv

lora.set_mode_rx()

while 1:
    pass
