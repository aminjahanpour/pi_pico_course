# INSTALL    ssd1306   FROM   Tools -> Manage packages...

from machine import Pin, I2C
import time
import ssd1306 # this is the library for the OLED



##############################################################
# OLED

i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)

# now we use the I2C object to define an OLED object
oled = ssd1306.SSD1306_SPI(
    128,    # width
    64,     # height
    i2c,
)





##############################################################
# SPLASH SCREEN

oled.fill(0)                        # clear the screen
oled.text("My Brand",    0, 0)      # write on x=0 and y=0 (top left corner)
oled.text("By me",       0, 20)     # write on x=0 and y=20 (middle left)
oled.text("ADC Live",    0, 40)     # write on x=40 and y=0 (bottom left)
oled.show()                         # display the drawings

time.sleep(2)


