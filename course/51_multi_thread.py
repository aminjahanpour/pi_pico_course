from machine import Pin
import time

import _thread


gpio15  =   Pin(15, Pin.OUT)
led     =   Pin(25, Pin.OUT)


def core_0_thread():
        
    while True:
        print("Thread #1 ")        
        led.toggle()
        time.sleep(1)



def core_1_thread():

    while True:
        print("Thread #2 ")        
        gpio15.toggle()
        time.sleep(2)

second_thread = _thread.start_new_thread(core_1_thread, ())

core_0_thread()
