
from machine import ADC, Pin
import time

# Voltage divider
R1 = 1_000       # 1k Ohm (top resistor)
R2 = 9_890      # 10k Ohm (bottom resistor)

# Pico ADC
adc = ADC(Pin(26))

adc_reference = 3.27

while True:

    # Read ADC
    adc_value = adc.read_u16() 

    # Convert ADC reading to voltage
    v_out = adc_value * adc_reference / 65535

    # Recover original input voltage
    v_in = v_out * (R1 + R2) / R2

    print("-------------------------")
    print("ADC Value:", adc_value)
    print("Vout:", round(v_out, 3), "V")
    print("Recovered Vin:", round(v_in, 3), "V")

    time.sleep(0.1)
