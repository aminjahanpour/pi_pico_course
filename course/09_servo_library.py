# INSTALL    micropython-servo   FROM   Tools -> Manage packages...

from machine import Pin, ADC
import time
from servo import Servo


pot_pin = ADC(Pin(26))



# now we are using the servo-dedicated library
# keep the signal pin on GPIO0
my_servo = Servo(pin_id=0)


# let's do some quick moves before getting into the loop
delay = 0.3

my_servo.write(0) # servo angle = 0
time.sleep(delay)

my_servo.write(90) # servo angle = 90
time.sleep(delay)

my_servo.write(180) # servo angle = 180
time.sleep(delay)

my_servo.write(270) # servo angle = 270
time.sleep(delay)

my_servo.write(360) # servo angle = 360
time.sleep(delay)


while True:
    
    # read the analog signal
    pot_value = pot_pin.read_u16()
    
    # simply map the 16-bit analog into [0 : 360] to get an angle
    servo_angle = int((pot_value / 65535) * 360)
        
    print(servo_angle)
    
    my_servo.write(servo_angle)
    
    # let's add some delay to keep things look smooth
    time.sleep(0.01)
