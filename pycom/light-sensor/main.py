# https://github.com/micropython/micropython-lib/blob/master/umqtt.simple/example_sub_led.py

import time
import pycom
from mqtt import MQTTClient
import ubinascii
import machine
import micropython
from pysense import Pysense
import LTR329ALS01
import ujson as json
import uasyncio as asyncio

# Wireless network
def connect_wifi():
    from network import WLAN      # For operation of WiFi network

    WIFI_SSID = "DarthGuest"
    WIFI_PASS = ""

    wlan = WLAN(mode=WLAN.STA)
    wlan.connect(WIFI_SSID, timeout=5000)
    time.sleep(3)

    while not wlan.isconnected(): # Code waits here until WiFi connects
        machine.idle()

    print("Connected to Wifi")
#connect_wifi() # only run if you run the file directly. When uploaded boot.py manages this

# BEGIN SETTINGS

#Light Sensor
py = Pysense()
light_sensor = LTR329ALS01.LTR329ALS01(py)

SAMPLING_STEP = 0.2 # seconds between each sample
SAMPLING_DURATION = 5 # seconds to gather samples for
SAMPLES_COUNT = SAMPLING_DURATION / SAMPLING_STEP

# Device
DEVICE_BUILDING = "home"
DEVICE_ROOM = "living-room"
DEVICE_ID = ubinascii.hexlify(machine.unique_id())  # Can be anything

# Broker settings
SERVER = "165.22.79.210"
PORT = 65020

SEP = '/'
ROOT_TOPIC = DEVICE_BUILDING + SEP + DEVICE_ROOM # building/room
AMBIENT_LIGHT_REQUEST_TOPIC = (ROOT_TOPIC + SEP + "ambient" + SEP + "request").encode('UTF-8') # building/room/ambient/request
AMBIENT_LIGHT_PUBLISH_TOPIC = (ROOT_TOPIC + SEP + "ambient" + SEP + "publish") # building/room/ambient/publish
# END SETTINGS

# Cache
is_sampling = False
last_sample = None
time_to_next = 0
cache_created = 0

loop = asyncio.get_event_loop()

# RGBLED
pycom.heartbeat(False)
time.sleep(0.1) # Workaround for a bug.
pycom.rgbled(0xff0000)  # Status red = not working


pycom.rgbled(0xffd700) # Status orange: partially working

# FUNCTIONS
def subscribe_request_ambient_light(topic, msg):
    if(topic == AMBIENT_LIGHT_REQUEST_TOPIC):
        try:
            msg = msg.decode('UTF-8')
            msg = json.loads(msg)
            loop.create_task(publish_ambient_light(msg))
        except:
            print('invalid message format')

def get_cache_age():
    return time.ticks_diff(time.ticks_ms(), cache_created)

def get_reply_msg(val, is_cache):
    msg = {}
    msg['value'] = val
    msg['age'] = get_cache_age()
    msg['isCache'] = is_cache
    return json.dumps(msg)

async def sample_ambient_light():
    global is_sampling, last_sample, time_to_next, cache_created
    is_sampling = True
    samples = []

    time_to_next = SAMPLING_DURATION
    while(time_to_next > 0.001):
        samples.append(light_sensor.light())
        time_to_next -= SAMPLING_STEP
        await asyncio.sleep(SAMPLING_STEP)

    res = 0
    for s in samples:
        res += s[0]

    res /= SAMPLES_COUNT

    last_sample = res
    cache_created = time.ticks_ms()
    client.publish(topic=AMBIENT_LIGHT_PUBLISH_TOPIC, msg=get_reply_msg(res, False))
    is_sampling = False

async def timeout(duration):
    await asyncio.sleep(duration)

async def check_for_messages():
    while(True):
        await asyncio.sleep(1)
        client.check_msg()

async def publish_ambient_light(msg):
    global is_sampling
    age = get_cache_age()
    if (is_sampling or age < msg['acceptedAge']) and last_sample is not None:
        client.publish(topic=AMBIENT_LIGHT_PUBLISH_TOPIC, msg=get_reply_msg(last_sample, True))
    else:
        loop.create_task(sample_ambient_light())


client = MQTTClient(DEVICE_ID, SERVER, PORT)
client.set_callback(subscribe_request_ambient_light)
client.connect()
client.subscribe(AMBIENT_LIGHT_REQUEST_TOPIC)
print("Connected to %s, subscribed to %s" % (SERVER, AMBIENT_LIGHT_REQUEST_TOPIC))

pycom.rgbled(0x006000) # Status green: connected successfully to broker

loop.create_task(check_for_messages()) # Required for new messages to be processedé
loop.run_forever()
