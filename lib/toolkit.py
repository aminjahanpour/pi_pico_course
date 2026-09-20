from machine import Pin, ADC
import utime

board_led = Pin(25, Pin.OUT)
sensor_temp = ADC(4)




def pico_led_blink():
    board_led(1)
    utime.sleep(0.3)
    board_led(0)


def read_pico_tempreture():
    temperature = sensor_temp.read_u16() * (3.3 / 65535)
    temperature = 27 - (temperature - 0.706) / 0.001721

    return temperature

def as7262_take_measurements(as7262_sensor):
    wavelengths = as7262_sensor.get_wavelengths()

    calibrated_values = [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0]
    as7262_sensor.take_measurements()
    calibrated_values = as7262_sensor.get_calibrated_values()

    return str([round(a/b,2) for (a,b) in zip(calibrated_values , wavelengths)]).replace(' ','')[1:-1]
