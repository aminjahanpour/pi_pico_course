from machine import I2C, Pin
from time import sleep
from i2c_lcd import I2cLcd

i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)

lcd = I2cLcd(i2c, 0x27, 2, 16)

lcd.clear()
lcd.putstr("Hello, Amin!")
lcd.move_to(0, 1)
lcd.putstr("LCD1602 + Pico")