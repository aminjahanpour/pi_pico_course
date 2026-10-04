# INSTALL    ssd1306   FROM   Tools -> Manage packages...

from machine import Pin, ADC, PWM, SPI
import time
import ssd1306 # this is the library for the OLED

pot_pin = ADC(Pin(26))

servo = PWM(Pin(15))

servo.freq(50)

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
oled.text("My Brand",    0, 0)      # write on x=0 and y=0 (top left corner)
oled.text("By me",       0, 20)     # write on x=0 and y=20 (middle left)
oled.text("ADC Live",    0, 40)     # write on x=40 and y=0 (bottom left)
oled.show()                         # display the drawings


time.sleep(4)

while True:
    
    pot_value = pot_pin.read_u16()
    
    pot_norm = pot_value / 65535

    # Map potentiometer to servo position
    duty_cycle = int(3277 + (pot_value / 65535) * (6554 - 3277))

    servo.duty_u16(duty_cycle)

    print(pot_norm, duty_cycle)
    time.sleep(0.02)
    
    oled.fill(0)
    oled.text(str(pot_norm), 0, 0)
    oled.show()
