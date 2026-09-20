import utime
from utime import sleep
import network
import urequests as requests
import json
from machine import Pin, I2C
import time

from microdot import Microdot
from ulora import create_lora

board_led = Pin(25, Pin.OUT)
board_led(1)
utime.sleep(0.3)
board_led(0)

# OLED
import ssd1306

# Heltec LoRa 32 with OLED Display
oled_width = 128
oled_height = 64
i2c_rst = Pin(16, Pin.OUT)
i2c_rst.value(0)
time.sleep_ms(5)
i2c_rst.value(1)
i2c_scl = Pin(15, Pin.OUT, Pin.PULL_UP)
i2c_sda = Pin(4, Pin.OUT, Pin.PULL_UP)
i2c = I2C(scl=i2c_scl, sda=i2c_sda)
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)
oled.fill(0)
oled.show()

server_url = 'http://192.168.0.12:5555/'
api_key = '0d80c5a7740ac8ff2fc29dc4a5d791b400161b21'


def oled_print(message):
    print(str(message))
    oled.fill(0)
    oled.text(str(message), 0, 0)
    oled.show()


oled_print('hi')

### lora
station_id = 1

lora = create_lora(this_address=station_id, mc='esp32')


### wifi

def talk_to_jason():
    payload = {
        'req': 'greetings',
        'key': api_key,
        'station_id': station_id,
    }

    resp = requests.post(url=server_url, json=payload)
    assert resp.status_code == 200
    ret = json.loads(resp.content.decode("utf-8"))['ret']
    oled_print(ret)


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    oled_print('connecting..')

    wlan.connect("onParkside", "P@RK$!de")
    while not wlan.isconnected():
        pass

oled_print(wlan.ifconfig()[0])

talk_to_jason()

########
# RECEIVER

asset_response = None
sensor_wait_time = 5
crew_action_wait_time = 5
a_payload_arrived = False

my_crews = []
my_sensors = []

crews_done = []
crews_outcomes = []

project_id = None
session_id = None


# This is our callback function that runs when a message is received
def on_recv(payload):
    global asset_response
    global a_payload_arrived
    global my_crews
    global crews_done
    global crews_outcomes
    global my_sensors
    global project_id
    global session_id

    oled_print('recieved')
    print(payload)

    # check to see if the message can be properly decoded
    if payload.header_from not in my_crews + my_sensors:
        oled_print('unknown header_from')
        return

    try:

        decoded_message = payload.message.decode()
        message = decoded_message.split(',')
        a_payload_arrived = True

        asset_response = message

    except:
        print('message can not be properly decoded')
        return


# set callback
lora.on_recv = on_recv

#### server app
app = Microdot()

"""
send one, wait for response, then send another one
this is slow by safe: order is respected
"""


def get_status(request_json):
    global asset_response
    global a_payload_arrived
    global my_crews
    global crews_done
    global crews_outcomes
    global my_sensors
    global project_id
    global session_id

    oled_print('reporting status')

    project_id = int(request_json['project_id'])
    session_id = int(request_json['session_id'])

    assets = request_json['station']

    results = {}


    for crew in assets['crew']:
        my_crews.append(int(crew['id']))

    my_crews = list(set(my_crews))

    for sensor in assets['sensor']:
        my_sensors.append(int(sensor['id']))

    my_sensors = list(set(my_sensors))

    asset_ids = my_crews + my_sensors

    for asset_id in asset_ids:

        a_payload_arrived = False
        asset_response = None

        lora.send(data='status', header_to=asset_id)
        lora.set_mode_rx()

        oled_print(f'send status {sensor}')


        start = time.ticks_ms()

        while a_payload_arrived == False and time.ticks_diff(time.ticks_ms(), start) / 1000 < sensor_wait_time:
            sleep(0.1)

        result = asset_response is not None

        results[asset_id] = result

    oled_print(results)

    return results


"""
send all at once, collect later
what if two sender send at the same time? then this goes wrong
"""


def dispatch(actions):
    global asset_response
    global a_payload_arrived
    global my_crews
    global crews_done
    global crews_outcomes
    global my_sensors
    global project_id
    global session_id


    results = {}

    for action in actions:

        a_payload_arrived = False
        asset_response = None

        lora.send(data=str(action['dv_values'])[1:-1], header_to=int(action['crew_id']))
        lora.set_mode_rx()

        oled_print(f"dispatch Crew {action['crew_id']} DVs:{action['dv_values']}")

        start = time.ticks_ms()

        while a_payload_arrived == False and time.ticks_diff(time.ticks_ms(), start) / 1000 < crew_action_wait_time:
            sleep(0.1)

        results[action['crew_id']] = asset_response

        oled_print(asset_response)

    return results




def read_sensors():
    global asset_response
    global a_payload_arrived
    global my_crews
    global crews_done
    global crews_outcomes
    global my_sensors
    global project_id
    global session_id

    oled_print('read sensors')

    results = {}

    for sensor in my_sensors:

        a_payload_arrived = False
        asset_response = None

        lora.send(data='read', header_to=int(sensor))
        lora.set_mode_rx()

        oled_print(f'ask sensor {sensor}...')


        start = time.ticks_ms()

        while a_payload_arrived == False and time.ticks_diff(time.ticks_ms(), start) / 1000 < sensor_wait_time:
            sleep(0.1)

        results[sensor] = asset_response

        oled_print(asset_response)

    return results


@app.route('/', methods=["GET"])
def get_handler(request):
    return 'Hello, world!'


@app.route('/', methods=["POST"])
def post_handler(request):
    request_json = request.json

    print(f"serving {request_json['req']}\n")
    print(request_json, '\n')

    if request_json['req'] == 'status':
        ret = get_status(request_json)
        return json.dumps({"ret": ret})

    elif request_json['req'] == 'dispatch':
        actions = request_json['actions']

        ret = dispatch(actions)
        return json.dumps({"ret": ret})

    elif request_json['req'] == 'read_sensors':
        ret = read_sensors()
        return json.dumps({"ret": ret})


app.run(host='192.168.0.15', port='80', debug=True)
