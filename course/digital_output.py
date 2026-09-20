from machine import Pin
import time


# set up GPIO16. This is the pin on bottom right.
gpio16 = Pin(16, Pin.OUT)

# Set up the onboard LED
# led = Pin("LED", Pin.OUT)


while True:
    
    gpio16.on()   # Flip GPIO16

    time.sleep(1)     # Wait 1 second

    gpio16.off()   # Flip GPIO16

    time.sleep(1)     # Wait 1 second


    #led.toggle()      # Switch LED on/off
    # time.sleep(1)     # Wait 1 second
