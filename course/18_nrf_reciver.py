from machine import Pin, SPI, PWM
from nrf24l01 import NRF24L01
import struct
import time




#######################################################################
# SETTING UP


led = Pin(25, Pin.OUT)



# NRF24L01
spi = SPI(
    0,                      # Select SPI interface 0 on the Raspberry Pi Pico
    baudrate=1_000_000,     # Set the SPI communication speed to 1 MHz
    polarity=0,             # Keep the clock low when idle (CPOL = 0)
    phase=0,                # Read data on the first clock edge (CPHA = 0)
    sck=Pin(18),            # Use GP18 as the SPI clock (SCK) pin
    mosi=Pin(19),           # Use GP19 to send data from the Pico to the radio
    miso=Pin(16)            # Use GP16 to send data from the device to the Pico
)


csn = Pin(20, Pin.OUT, value=1)
ce = Pin(17, Pin.OUT, value=0)


radio = NRF24L01(          # Create and configure the nRF24L01 radio object
    spi,                   # SPI interface used to communicate with the radio
    csn,                   # Chip Select pin: selects the radio for SPI communication
    ce,                    # Chip Enable pin: controls the radio's operating mode
    channel=46,             # Set the wireless channel to 46
    payload_size=8          # Set each data packet to 8 bytes
)                          # Finish creating the radio object






#######################################################################
# INITIALIZE


radio.open_rx_pipe(0, b"NODE2")
radio.start_listening()


print()
print("==============================")
print("JOYSTICK RECEIVER READY")
print("==============================")

print("CONFIG    :", hex(radio.reg_read(0x00)))
print("EN_RXADDR :", hex(radio.reg_read(0x02)))
print("RF_CH     :", hex(radio.reg_read(0x05)))
print("RF_SETUP  :", hex(radio.reg_read(0x06)))




pwm_pin_left  = PWM(Pin(21))
pwm_pin_right = PWM(Pin(22))

pwm_pin_left.freq( 20000)
pwm_pin_right.freq(20000)


left_duty_cycle = 0
right_duty_cycle = 0

left_duty_cycle_new = 0
right_duty_cycle_new = 0

counter = 0





#######################################################################
# MAIN LOOP

while True:

    counter = counter + 1

    if counter % 100 == 0:
        led.toggle()
        counter = 0


    # update the duty cycle only if it is a new value
    if left_duty_cycle_new != left_duty_cycle:
        pwm_pin_left.duty_u16(left_duty_cycle_new)
        left_duty_cycle_new = left_duty_cycle
        
        
    # update the duty cycle only if it is a new value
    if right_duty_cycle_new != right_duty_cycle:
        pwm_pin_right.duty_u16(right_duty_cycle_new)
        right_duty_cycle_new = right_duty_cycle
        

    if radio.any():

        data = radio.recv()

        # Unpack:
        #   2 bytes X
        #   2 bytes Y
        #   1 byte button
        x, y, sw = struct.unpack("<HHB", data[:5])

        print(
            "X:", x,
            "Y:", y,
            "SW:", sw
        )

        left_duty_cycle_new = x
        right_duty_cycle_new = y
        
        time.sleep_ms(10)




    time.sleep_ms(10)

