
from machine import Pin, SPI, ADC
from nrf24l01 import NRF24L01
import struct
import time



#######################################################################
# SETTING UP


led = Pin(25, Pin.OUT)

# JOYSTICK
x_axis = ADC(Pin(26))
y_axis = ADC(Pin(27))
button = Pin(15, Pin.IN, Pin.PULL_UP)

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
ce  = Pin(17, Pin.OUT, value=0)

radio = NRF24L01(          # Create and configure the nRF24L01 radio object
    spi,                   # SPI interface used to communicate with the radio
    csn,                   # Chip Select pin: selects the radio for SPI communication
    ce,                    # Chip Enable pin: controls the radio's operating mode
    channel=46,             # Set the wireless channel to 46
    payload_size=8          # Set each data packet to 8 bytes
)                          






#######################################################################
# INITIALIZE

radio.open_tx_pipe(b"NODE1")
radio.stop_listening()

print("TRANSMITTER READY")
print("CONFIG:",    hex(radio.reg_read(0x00)))
print("RF_CH:",     hex(radio.reg_read(0x05)))
print("RF_SETUP:",  hex(radio.reg_read(0x06)))

counter_ = 0








#######################################################################
# MAIN LOOP


while True:

    counter_ += 1

    if counter_ >= 2:
        led.toggle()
        counter_ = 0

    # Read joystick
    x = x_axis.read_u16()
    y = y_axis.read_u16()
    sw = button.value()

    # Transmit X, Y, and SW only
    # 2 bytes + 2 bytes + 1 byte + 3 padding bytes = 8 bytes
    message = struct.pack("<HHBxxx", x, y, sw)

    attempts = 0

    while True:
        attempts += 1

        try:
            radio.send(message)

            print(
                "SUCCESS:",
                "X:", x,
                "Y:", y,
                "SW:", sw,
                "attempts:", attempts
            )
            break

        except OSError as e:
            print(
                "RETRY:",
                "attempt:", attempts,
                "error:", e
            )
            time.sleep_ms(20)

    time.sleep_ms(100)

