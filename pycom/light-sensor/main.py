# https://github.com/micropython/micropython-lib/blob/master/umqtt.simple/example_sub_led.py

from network import WLAN      # For operation of WiFi network
import time                   # Allows use of time.sleep() for delays
import pycom                  # Base library for Pycom devices
from mqtt import MQTTClient  # For use of MQTT protocol to talk to Adafruit IO
import ubinascii              # Needed to run any MicroPython code
import machine                # Interfaces with hardware components
import micropython            # Needed to run any MicroPython code
#import bh1750fvi
from pysense import Pysense
import LTR329ALS01

import uasyncio as asyncio

# BEGIN SETTINGS

#Light Sensor
#i2c = I2C(0, I2C.MASTER, baudrate=100000)
#light_sensor = bh1750fvi.BH1750FVI(i2c, addr=i2c.scan()[0])
py = Pysense()
light_sensor = LTR329ALS01.LTR329ALS01(py)

SAMPLING_STEP = 0.2 # seconds between each sample
SAMPLING_DURATION = 5 # seconds to gather samples for
SAMPLES_COUNT = SAMPLING_DURATION / SAMPLING_STEP

# Device
DEVICE_BUILDING = "home"
DEVICE_ROOM = "living-room"
DEVICE_ID = ubinascii.hexlify(machine.unique_id())  # Can be anything

# Wireless network
WIFI_SSID = "DarthGuest"
WIFI_PASS = "" # No this is not our regular password. :)

# Broker settings
SERVER = "165.22.79.210"
PORT = 65020

SEP = '/'
ROOT_TOPIC = DEVICE_BUILDING + SEP + DEVICE_ROOM
AMBIENT_LIGHT_REQUEST_TOPIC = (ROOT_TOPIC + SEP + "ambient" + SEP + "request").encode('UTF-8')
AMBIENT_LIGHT_PUBLISH_TOPIC = (ROOT_TOPIC + SEP + "ambient" + SEP + "publish")
# END SETTINGS

# Cache
is_sampling = False
last_sample = None

# RGBLED
pycom.heartbeat(False)
time.sleep(0.1) # Workaround for a bug.
pycom.rgbled(0xff0000)  # Status red = not working

# WIFI
wlan = WLAN(mode=WLAN.STA)
wlan.connect(WIFI_SSID, timeout=5000)
time.sleep(3)

while not wlan.isconnected(): # Code waits here until WiFi connects
    machine.idle()

print("Connected to Wifi")
pycom.rgbled(0xffd700) # Status orange: partially working

# FUNCTIONS
def subscribe_request_ambient_light(topic, msg):
    if(topic == AMBIENT_LIGHT_REQUEST_TOPIC):
        publish_ambient_light()

def sample_ambient_light():
    is_sampling = True
    samples = []

    duration = SAMPLING_DURATION
    while(duration > 0):
        print('sampling...')
        samples.append(light_sensor.light())
        duration -= SAMPLING_STEP
        #await asyncio.sleep(SAMPLING_STEP)
        time.sleep(SAMPLING_STEP)
        #client.check_msg() # causes stack overflow

    res = 0
    for s in samples:
        res += s[0]
        print(s)

    res /= SAMPLES_COUNT

    last_sample = res
    is_sampling = False
    return res

def publish_ambient_light():
    if is_sampling:
        if(last_sample == None):
            print('no cache available')
            return
        client.publish(topic=AMBIENT_LIGHT_PUBLISH_TOPIC, msg=str(last_sample))
        print('using cache')
    else:
        print('awaiting')
        #val = await sample_ambient_light()
        val = sample_ambient_light()
        client.publish(topic=AMBIENT_LIGHT_PUBLISH_TOPIC, msg=str(val))
        print('published new sample')


client = MQTTClient(DEVICE_ID, SERVER, PORT)
client.set_callback(subscribe_request_ambient_light)
client.connect()
client.subscribe(AMBIENT_LIGHT_REQUEST_TOPIC)
print("Connected to %s, subscribed to %s" % (SERVER, AMBIENT_LIGHT_REQUEST_TOPIC))

pycom.rgbled(0x006000) # Status green: connected successfully to broker

try:
    while 1:
        client.check_msg()
finally:
    client.disconnect()
    client = None
    wlan.disconnect()
    wlan = None
    pycom.rgbled(0x000022) # Status blue: stopped
    print("Disconnected from server and wlan")
