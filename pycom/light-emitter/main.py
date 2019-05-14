# https://github.com/micropython/micropython-lib/blob/master/umqtt.simple/example_sub_led.py

import time
import pycom
from mqtt import MQTTClient
import ubinascii
import machine
import micropython
from pysense import Pysense
import ujson as json

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
# Device
DEVICE_BUILDING = "home"
DEVICE_ROOM = "living-room"
DEVICE_ID = ubinascii.hexlify(machine.unique_id())  # Can be anything

# Broker settings
SERVER = "165.22.79.210"
PORT = 65020

SEP = '/'
ROOT_TOPIC = DEVICE_BUILDING + SEP + DEVICE_ROOM # building/room
LIGHT_TOPIC = (ROOT_TOPIC + SEP + "light").encode('UTF-8') # building/room/light
REGISTRATION_TOPIC = 'device-registration'
RE_REGISTRATION_TOPIC = 'registration-request'.encode('UTF-8')
# END SETTINGS

color = '0x444444'
intensity = 255

# RGBLED
pycom.heartbeat(False)
time.sleep(0.1) # Workaround for a bug.
pycom.rgbled(0xff0000)  # Status red = not working

expected = "{ \"color\": { \"r\": 255, \"g\": 0, \"b\": 0 }, \"intensity\": 255 }"
'''
{
    "color": {
        "r": 255,
        "g": 0,
        "b": 0
    }
    "intensity": 255
}
'''
# FUNCTIONS

def validate_msg(msg):
    if not ('color' in msg and 'intensity' in msg and 'r' in msg['color'] and 'g' in msg['color'] and 'b' in msg['color']):
        raise Exception('')

def to_hex(color):
    modifier = intensity / 255
    return '0x{:02x}{:02x}{:02x}'.format(int(color['r'] * modifier), int(color['g'] * modifier), int(color['b'] * modifier))

def registration_msg():
    msg = {}
    msg['id'] = DEVICE_ID
    msg['location'] = ROOT_TOPIC
    msg['deviceType'] = 'light'

    return json.dumps(msg)

def register():
    client.publish(topic=REGISTRATION_TOPIC, msg=registration_msg())

def subscribe_light(topic, msg):
    global color, intensity
    if topic == RE_REGISTRATION_TOPIC:
        register()
    elif topic == LIGHT_TOPIC:
        msg = msg.decode('UTF-8')
        try:
            message = json.loads(msg)
        except:
            print('invalid json format')
            return
        try:
            validate_msg(message)
        except:
            print('invalid message contents')
            print('expected: ' + expected)
            print('received: ' + msg)
            return

        # Configure light
        intensity = message['intensity']
        color = to_hex(message['color'])
        pycom.rgbled(int(color))
        print('setting color to ' + color)

client = MQTTClient(DEVICE_ID, SERVER, PORT)
client.set_callback(subscribe_light)
client.connect()
client.subscribe(LIGHT_TOPIC)
client.subscribe(RE_REGISTRATION_TOPIC)

register()

print("Connected to %s, subscribed to %s" % (SERVER, LIGHT_TOPIC))

pycom.rgbled(0x006000) # Status green: connected successfully to broker

#try:
while 1:
    client.check_msg()
    time.sleep(1)
# finally:
#     client.disconnect()
#     client = None
#     wlan.disconnect()
#     wlan = None
#     pycom.rgbled(0x000022)# Status blue: stopped
