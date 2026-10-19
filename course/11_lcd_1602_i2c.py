from machine import I2C, Pin
from lcd1602 import LCD

i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)

# 0 → I2C bus number. The Pico has I2C(0) and I2C(1).
# scl=Pin(5) → SCL (clock) is connected to GP5.
# sda=Pin(4) → SDA (data) is connected to GP4.
# freq=400000 → I2C clock frequency = 400 kHz.

lcd = LCD(i2c, addr=0x27)
# 0x27 is the I2C address of the LCD's backpack


lcd.clear()
lcd.write(0, 0, "Hello, John!")
lcd.write(0, 1, "LCD1602 + Pico")