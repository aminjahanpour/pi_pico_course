from machine import Pin, PWM
import time

# Passive buzzer on GPIO16
buzzer = PWM(Pin(16))

# 50% duty cycle
buzzer.duty_u16(32768)

# Musical note frequencies (Hz)
G4 = 392
A4 = 440
B4 = 494
C5 = 523
D5 = 587
E5 = 659
F5 = 698
G5 = 784

# Happy Birthday melody
# (frequency, duration)

tune = [
    # Happy birthday to you
    (G4, 0.3), (G4, 0.3), (A4, 0.6),
    (G4, 0.6), (C5, 0.6), (B4, 1.0),

    # Happy birthday to you
    (G4, 0.3), (G4, 0.3), (A4, 0.6),
    (G4, 0.6), (D5, 0.6), (C5, 1.0),

    # Happy birthday dear friend
    (G4, 0.3), (G4, 0.3), (G5, 0.6),
    (E5, 0.6), (C5, 0.6), (B4, 0.6),
    (A4, 1.0),

    # Happy birthday to you
    (F5, 0.3), (F5, 0.3), (E5, 0.6),
    (C5, 0.6), (D5, 0.6), (C5, 1.2)
]

while True:

    for frequency, duration in tune:

        buzzer.freq(frequency)
        buzzer.duty_u16(32768)

        time.sleep(duration)

        # Brief silence between notes
        buzzer.duty_u16(0)
        time.sleep(0.05)

    # Silence before repeating
    time.sleep(3)