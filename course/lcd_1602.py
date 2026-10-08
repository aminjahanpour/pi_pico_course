from machine import I2C, Pin
from lcd import LCD

i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)

lcd = LCD(i2c, addr=0x27)

lcd.clear()
lcd.write(0, 0, "Hello, Amin!")
lcd.write(0, 1, "LCD1602 + Pico")