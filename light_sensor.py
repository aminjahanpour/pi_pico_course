from machine import I2C, Pin
from AS726X import AS726X
import time

i2c_scl = Pin(1, Pin.OUT, Pin.PULL_UP)
i2c_sda = Pin(0, Pin.OUT, Pin.PULL_UP)
i2c = I2C(0, scl=i2c_scl, sda=i2c_sda)

as7262_sensor = AS726X(i2c=i2c)

sensor_type = as7262_sensor.get_sensor_type()


print(as7262_sensor.get_wavelengths())

while True:
    calibrated_values = [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0]
    try:
        as7262_sensor.take_measurements()
        calibrated_values = as7262_sensor.get_calibrated_values()

    except Exception as error:
        print(error)

    print("{sensor_type}:{ch0},{ch1},{ch2},{ch3},{ch4},{ch5}".format(
        sensor_type=sensor_type, ch0=calibrated_values[0],
        ch1=calibrated_values[1], ch2=calibrated_values[2],
        ch3=calibrated_values[3], ch4=calibrated_values[4],
        ch5=calibrated_values[5]))

    # time.sleep(0.1)
