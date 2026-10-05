from machine import Pin, ADC
import time

# this is our go-to pin for analog signals
potentiometer = ADC(Pin(26))

while True:

    
    # let's get the raw data first
    adc_raw_value = potentiometer.read_u16()

    # the raw data ranges from 0 to 65535 so let's normalize it
    # 65535 is actually 2 to the power of 16 (menus 1)
    # this is because the ADC hardware on Pico has a resolution of 16 bits on it
    adc_normalized_value = adc_raw_value / 65535

    # now let's map to 3.3v to get the voltage
    voltage = adc_normalized_value * 3.3

    print(voltage)

    # add a small delay
    time.sleep(0.01)

    