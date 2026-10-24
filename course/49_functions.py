from machine import Pin, ADC, PWM
import time


led = Pin("LED", Pin.OUT)



def led_blink_animation():
    led.on()
    time.sleep_ms(100)
    led.off()
    time.sleep_ms(200)
    led.on()
    time.sleep_ms(300)
    led.off()
    time.sleep_ms(100)
    led.on()
    time.sleep_ms(100)
    led.off()


# led_blink_animation won't run unless we call it like in below:
# once it finishes the function, it returns right back here

# some variable
a = 2

led_blink_animation()

# some other varable
b = 3



####################################################################
# ARGUMENTS


# the arguments are our way to input the data in the function
def add(num_1, num_2):
    
    # here we do some calculation
    answer = num_1 + num_2
    
    # this is how we get the data out of the function
    return answer



result = add(4, 5)

print(f"result = {result}")



######################################################################
# LOCAL VARIABLES

def test_function():
    x = 1


x = 2

test_function()

# what value is x?
print(f"x = {x}")



######################################################################
# GLOBAL VARIABLES

# g is a global variable because it is not in any functions. it is at the root level
# a global varlbe can be directly accessed from withing other functions
g = 100



def test_function_2():
    global g
    return g + 1


ans = test_function_2()
print(f"ans = {ans}")




    
