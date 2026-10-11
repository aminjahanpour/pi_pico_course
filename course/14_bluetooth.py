from machine import UART, Pin
import time


led = Pin(25, Pin.OUT)

uart = UART(
    0,                 # UART bus number: UART0 (Pico has UART0 and UART1)
    baudrate=9600,     # Communication speed: 9600 bits per second
    tx=Pin(0),         # TX (transmit) uses GPIO 0: sends data to HC-06 RXD
    rx=Pin(1)          # RX (receive) uses GPIO 1: receives data from HC-06 TXD
)


counter = 0

while True:
        
    counter += 1

    if counter % 100 == 0:
        led.toggle()
        if counter > 100000:
            counter = 0

        # write a message on the UART, which in this case goes to the HC-06
        uart.write(f"Hello from Pico! {counter}\n")

    
    # see if any fresh data has arrived on the UART buffer    
    if uart.any():

        # read the newly arrived data from the buffer
        data = uart.read()

        print(data)
        
        
    time.sleep_ms(10)
