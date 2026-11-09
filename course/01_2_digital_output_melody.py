from machine import Pin
import time

# GPIO15 as digital output
gpio15 = Pin(15, Pin.OUT)

# Tempo
beat = 0.6  # seconds per beat

# Each number represents flash duration in beats
# Each phrase represents one line of Happy Birthday

melody = [
    # Happy birthday to you
    [0.5, 0.5, 1, 1, 1, 2],

    # Happy birthday to you
    [0.5, 0.5, 1, 1, 1, 2],

    # Happy birthday dear friend
    [0.5, 0.5, 1, 1, 1, 0.5, 1.5],

    # Happy birthday to you
    [0.5, 0.5, 1, 1, 1, 2]
]

while True:

    for phrase in melody:

        for duration in phrase:

            # LED ON
            gpio15.on()
            time.sleep(duration * beat * 0.7)

            # LED OFF
            gpio15.off()
            time.sleep(duration * beat * 0.3)

        # Pause between phrases
        time.sleep(0.5)

    # Pause before repeating
    time.sleep(2)
