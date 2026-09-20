from machine import Pin, I2C, PWM
# from AS726X import AS726X
from lib import toolkit
from ulora import create_lora
import time

# greetings
toolkit.pico_led_blink()

this_address = 2

lora = create_lora(this_address=this_address)

# Crew specific
# yellow_led = machine.PWM(machine.Pin(14))
# white_led = machine.PWM(machine.Pin(15))
# yellow_led.freq(1000)
# yellow_led.duty_u16(1000)
# white_led.freq(1000)
# white_led.duty_u16(1000)

led_r = PWM(Pin(13))
led_g = PWM(Pin(14))
led_b = PWM(Pin(15))

led_r.freq(1000)
led_g.freq(1000)
led_b.freq(1000)

led_r.duty_u16(0)
led_g.duty_u16(0)
led_b.duty_u16(0)



i2c_scl = Pin(1, Pin.OUT, Pin.PULL_UP)
i2c_sda = Pin(0, Pin.OUT, Pin.PULL_UP)
i2c = I2C(0, scl=i2c_scl, sda=i2c_sda)

# as7262_sensor = AS726X(i2c=i2c)


def perform_dvs(dvs):

    unpacked_dv_0 = int(dvs[0] * pow(2, 16))
    unpacked_dv_1 = int(dvs[1] * pow(2, 16))
    unpacked_dv_2 = int(dvs[2] * pow(2, 16))

    for i in range(3):
        outcome = False

        try:

            led_r.duty_u16(unpacked_dv_0)
            led_g.duty_u16(unpacked_dv_1)
            led_b.duty_u16(unpacked_dv_2)

            time.sleep(0.1)

            assert abs(led_r.duty_u16() - unpacked_dv_0) < 100
            assert abs(led_g.duty_u16() - unpacked_dv_1) < 100
            assert abs(led_b.duty_u16() - unpacked_dv_2) < 100

            outcome = True
            break

        except:
            print('error on implementing dvs')
            outcome = False

        time.sleep(0.1)

    return outcome

def on_recv(payload):
    toolkit.board_led.on()

    print(payload)

    message = payload.message.decode()

    if message == 'status':
        lora.send(data='online', header_to=1)
        print('sent status=online to Station')

    elif message == 'read':
        sensor_values = read()

        time.sleep(0.1)

        print(sensor_values)

        lora.send(data=f'read,{sensor_values}', header_to=1)

        print('sent sensor_values to Station')

    else:
        dvs = [float(x) for x in message.split(',')]

        outcome = perform_dvs(dvs)

        time.sleep(0.1)

        outcome = 'complete' if outcome else 'failed'

        print(outcome)

        lora.send(data=f'action_done,{outcome}', header_to=1)

        print('sent outcome to Station')

    lora.set_mode_rx()

    toolkit.board_led.off()


lora.on_recv = on_recv


def read():


    for i in range(3):
        sensor_values = 'error'

        # try:
        measurement = toolkit.as7262_take_measurements(as7262_sensor)

        time.sleep(0.1)

        assert measurement is not None

        sensor_values = measurement
        break

        # except:
        #     print('error on sensing')

        time.sleep(0.1)

    return sensor_values







# initially asset is set to receive messages from statio
lora.set_mode_rx()

