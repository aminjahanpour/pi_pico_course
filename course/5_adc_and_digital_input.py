
from machine import Pin, ADC
import time

button = Pin(14, Pin.IN, Pin.PULL_UP)

# we only have three pins on Pico that can read analog signal
# Pin 26, 27, and 28
# in this example, let's use Pin 26

potentiameter = ADC(Pin(26))

while True:

    if button.value() == 0:

        # let's get the raw data first
        adc_raw_value = potentiameter.read_u16()

        # the raw data ranges from 0 to 65535 so let's normalize it
        # 65535 is actually 2 to the power of 16 (menus 1)
        # this is because the ADC hardware on Pico has a resolution of 16 bits on it
        adc_normalized_value = adc_raw_value / 65535

        # now adc_normalized_value varies in between 0 and 1
        # if we multiple the normalized value by 3.3, we get the actual voltage reading
        adc_voltage = adc_normalized_value * 3.3


        print(adc_voltage)

    time.sleep(0.01)

    

