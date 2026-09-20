from machine import SoftI2C, SoftSPI, Pin, UART
from pyb import Timer
import struct
import utime


from nrf24l01 import NRF24L01

_RX_POLL_DELAY = const(15)
_SLAVE_SEND_DELAY = const(10)
pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")

csn = Pin("PB12", mode=Pin.OUT, value=1)
ce = Pin("PA8", mode=Pin.OUT, value=0)
spi = SoftSPI(sck="PB13", mosi="PB15", miso="PB14")
nrf = NRF24L01(spi, csn, ce, payload_size=12)

nrf.open_tx_pipe(pipes[0])
nrf.open_rx_pipe(1, pipes[1])
nrf.start_listening()


#UART
# uart = UART(1 , 9600 )
# uart.init(9600)
# uart.write('hello')
# print(uart.readchar())
# print(uart.any())
# print('over')
# # LED
# led = Pin("PA0", Pin.OUT)
# led.high()
# led.low()
# 
# 
# # PWM
# 
# pwm_pin_1 = Pin('PA0', Pin.OUT)
# pwm_pin_2 = Pin('PA1', Pin.OUT)

esc_min = 48000  # (5%) use when setting the PWM pin to avoid reconfiguration


pwm_pin_1 = Pin('B4', Pin.OUT)  # blue
pwm_pin_2 = Pin('A15', Pin.OUT)  # yellow
pwm_pin_3 = Pin('B4', Pin.OUT)  # green
pwm_pin_4 = Pin('A15', Pin.OUT)  # blue


freq = 50

timer_2 = Timer(2, freq=50)
timer_3 = Timer(3, freq=50)
esc_1 = timer_3.channel(1, Timer.PWM, pin=pwm_pin_1, pulse_width=esc_min)
esc_2 = timer_2.channel(1, Timer.PWM, pin=pwm_pin_2, pulse_width=esc_min)
esc_3 = timer_3.channel(1, Timer.PWM, pin=pwm_pin_3, pulse_width=esc_min)
esc_4 = timer_2.channel(1, Timer.PWM, pin=pwm_pin_4, pulse_width=esc_min)



# timer_2_channel_1 = timer_2.channel(1, Timer.PWM, pin=pwm_pin_1, pulse_width_percent=0)
# timer_2_channel_2 = timer_2.channel(2, Timer.PWM, pin=pwm_pin_2, pulse_width_percent=0)
#
# timer_2_channel_1.pulse_width_percent(0)
# print(f'0%: {timer_2_channel_1.pulse_width()}')
#
# timer_2_channel_1.pulse_width_percent(5)
# print(f'5%: {timer_2_channel_1.pulse_width()}')
#
# timer_2_channel_1.pulse_width_percent(10)
# print(f'10%: {timer_2_channel_1.pulse_width()}')
#
#
# timer_2_channel_1.pulse_width_percent(100)
# print(f'100%: {timer_2_channel_1.pulse_width()}')

"""
a full period is broken into (48 * 10^6 / freq) width.
so the pulse with can vary between 0 and that number one by one.

"""

# print(int(48000000 / freq))

# timer_2_channel_2.pulse_width_percent(50)

#

nrf.stop_listening()
while True:
    
    # keep trying to send until you can
    nrf.send(struct.pack("fff", 1., 2., 3.))
    
    utime.sleep(0.3)




# while True:
# 
#     if nrf.any():
#         while nrf.any():
# 
#             buf = nrf.recv()
#             v_1, v_2, v_3 = struct.unpack("iii", buf)
# 
#             print(v_1, v_2, v_3)

            # utime.sleep_ms(_RX_POLL_DELAY)
            # utime.sleep_ms(_SLAVE_SEND_DELAY)
            #nrf.start_listening()
