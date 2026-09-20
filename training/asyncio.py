import machine
import uasyncio
import utime
import queue

# settings
led = machine.Pin(25, machine.Pin.OUT)
btn = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)
led_yellow = machine.Pin(13, machine.Pin.OUT)
led_blue = machine.Pin(12, machine.Pin.OUT)

led_yellow.off()


# co-routine: blink on a time
async def blink(q):
    delay_ms = 0
    while True:

        # check if there are messages in the queue
        if not q.empty():
            delay_ms = await q.get()
        led.toggle()

        # the scheduler will not automatically switch in between co-routines
        # await is used to do two things at the same time:

        #    1- yield to the scheduler
        #    2- wait for the command to finish

        await uasyncio.sleep_ms(delay_ms)

async def yellow_blink():
    while True:
        led_yellow.toggle()
        await uasyncio.sleep_ms(100)

async def blue_blink():
    while True:
        led_blue.toggle()
        await uasyncio.sleep_ms(200)


# co-routine: this function does nothing. it waits.
# only returns on button press

async def wait_button():
    btn_prev = btn.value()
    # btn.value() == btn_prev means nothing has happened
    # so putting it on a 'while' implies waiting
    # so in below we are saying, if nothing has happened yet,
    # just sleeps while also allowing other tasks to perform
    while (btn.value() == 1) or (btn.value() == btn_prev):
        btn_prev = btn.value()

        # here we only wait which means we sleep
        # but also to play nice to other tasks we also yield,
        # to do so, you need to use uasyncio.sleep not utime.sleep
        await uasyncio.sleep(0.04)

    """
    so this is a layout for a typical side task:
    
    async def side_task():
        while still_waiting_for_an_event():
            await uasyncio.sleep(0.04)
    """

    # return is implied in here


# co-routine: entry point for scyncio program
async def main():
    """
    this is our entry point
    from here we can spawn multiple co-routines

    this builds a future object; does not run anything
    blink(0.2)

    this will wait for the function blink to FINISH, which never happens
    so we get stuck here
    await blink(0.2)
    """

    # queue for passing messages
    q = queue.Queue()

    """
    uasyncio.create_task(co-routine)
    starts the co-routine as a task and immediately returns
    this is used for a passive background task which we want to
    run constantly in the background
    """
    # task with queue parameter
    uasyncio.create_task(blink(q))

    # tasks without queue parameter
    uasyncio.create_task(yellow_blink())
    uasyncio.create_task(blue_blink())

    """
    while
        await co-routine()
        
    is another way to launch background tasks but with more interactions.
    """


    # Main loop (never yeilds)
    timestamp = utime.ticks_ms()

    while True:

        await wait_button()

        # calculate time between button presses
        new_time = utime.ticks_ms()
        delay_time = new_time - timestamp
        timestamp = new_time
        print(delay_time)
        delay_time = min(delay_time, 2000)

        # send calculated time to blink task
        await q.put(delay_time)


# start even loop and run entry point co-routine
uasyncio.run((main()))
