from machine import Pin, ADC
import time

potentiameter = ADC(Pin(26))

while True:
    print(potentiameter.read_u16()/19860)
    time.sleep(0.01)

    