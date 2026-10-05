# INSTALL    ssd1306   FROM   Tools -> Manage packages...

from machine import Pin, SPI
import ssd1306 # this is the library for the OLED

# let's use the OLED library to define an SPI object
spi = SPI(
    0,
    baudrate=   10_000_000,
    polarity=   0,
    phase=      0,
    sck=        Pin(18),
    mosi=       Pin(19)
)

dc =    Pin(21) # Data/Command
res =   Pin(20) # Reset
cs =    Pin(17) # Chip Select

# now we use the SPI object to define an OLED object
oled = ssd1306.SSD1306_SPI(
    128,    # width
    64,     # height
    spi,
    dc,
    res,
    cs
)

oled.fill(0)                        # clear the screen
oled.text("Hello Pico!",    0, 0)   # write on x=0 and y=0 (top left corner)
oled.text("SPI OLED",       0, 20)  # write on x=0 and y=20 (middle left)
oled.text("Working!",       0, 40)  # write on x=40 and y=0 (bottom left)
oled.show()                         # display the drawings
