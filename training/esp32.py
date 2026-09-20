import machine
import uasyncio
import utime
import esp
import network
import urequests as requests
import json

from microWebSrv import MicroWebSrv

esp.osdebug(None)



def get_a_quote():
    ret = requests.get(url='https://quotes.rest/qod?language=en')
    assert ret.status_code == 200
    ret = json.loads(ret.content.decode("utf-8"))
    print(ret['contents']['quotes'][0]['quote'])

def talk_to_jason():
    server = 'http://192.168.0.12:5555/'

    key = '0d80c5a7740ac8ff2fc29dc4a5d791b400161b21'
    payload = {
        'req': 'greetings',
        'key': key,
    }

    resp = requests.post(url=server, json=payload)
    assert resp.status_code == 200
    ret = json.loads(resp.content.decode("utf-8"))['ret']
    print(ret)


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print('connecting to network...')
    wlan.connect("onParkside", "P@RK$!de")
    while not wlan.isconnected():
        pass
print('network config:', wlan.ifconfig())

# get_a_quote()
talk_to_jason()



mws = MicroWebSrv()      # TCP port 80 and files in /flash/www
mws.Start(threaded=True) # Starts server in a new thread

@MicroWebSrv.route('/get-test')
def handlerFuncGet(httpClient, httpResponse) :
  print("In GET-TEST HTTP")

@MicroWebSrv.route('/post-test', 'POST')
def handlerFuncPost(httpClient, httpResponse) :
  print("In POST-TEST HTTP")
