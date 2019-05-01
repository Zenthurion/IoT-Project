# https://github.com/micropython/micropython-lib/blob/master/umqtt.simple/example_sub_led.py

from network import WLAN      # For operation of WiFi network
import time                   # Allows use of time.sleep() for delays
import pycom                  # Base library for Pycom devices
from mqtt import MQTTClient  # For use of MQTT protocol to talk to Adafruit IO
import ubinascii              # Needed to run any MicroPython code
import machine                # Interfaces with hardware components
import micropython            # Needed to run any MicroPython code

# BEGIN SETTINGS
# These need to be change to suit your environment
RANDOMS_INTERVAL = 5000 # milliseconds
last_random_sent_ticks = 0  # milliseconds

# Wireless network
WIFI_SSID = "DarthGuest"
WIFI_PASS = "" # No this is not our regular password. :)

# Broker settings
SERVER = "165.22.79.210"
PORT = 65020
CLIENT_ID = ubinascii.hexlify(machine.unique_id())  # Can be anything
TEMP_TOPIC = "temp"
# END SETTINGS

# RGBLED
# Disable the on-board heartbeat (blue flash every 4 seconds)
# We'll use the LED to respond to messages from Adafruit IO
pycom.heartbeat(False)
time.sleep(0.1) # Workaround for a bug.
                # Above line is not actioned if another
                # process occurs immediately afterwards
pycom.rgbled(0xff0000)  # Status red = not working

# WIFI
# We need to have a connection to WiFi for Internet access
# Code source: https://docs.pycom.io/chapter/tutorials/all/wlan.html

wlan = WLAN(mode=WLAN.STA)
wlan.connect(WIFI_SSID, timeout=5000)

time.sleep(3)
#while not wlan.isconnected():    # Code waits here until WiFi connects
#    machine.idle()

print("Connected to Wifi")
pycom.rgbled(0xffd7000) # Status orange: partially working

# FUNCTIONS
def random_integer(upper_bound):
    return machine.rng() % upper_bound

def send_random():
    global last_random_sent_ticks
    global RANDOMS_INTERVAL

    if ((time.ticks_ms() - last_random_sent_ticks) < RANDOMS_INTERVAL):
        return; # Too soon since last one sent.

    some_number = random_integer(100)
    print("Publishing: {0} to {1} ... ".format(some_number, TEMP_TOPIC), end='')
    try:
        client.publish(topic=TEMP_TOPIC, msg=str(some_number))
        print("DONE")
    except Exception as e:
        print("FAILED")
    finally:
        last_random_sent_ticks = time.ticks_ms()

# Use the MQTT protocol to connect to Adafruit IO
client = MQTTClient(CLIENT_ID, SERVER, PORT)

# Subscribed messages will be delivered to this callback
#client.set_callback(sub_cb)
client.connect()
#client.subscribe(AIO_CONTROL_FEED)
#print("Connected to %s, subscribed to %s topic" % (SERVER, AIO_CONTROL_FEED))

pycom.rgbled(0x00ff00) # Status green: online to Adafruit IO

try:                      # Code between try: and finally: may cause an error
                          # so ensure the client disconnects the server if
                          # that happens.
    while 1:              # Repeat this loop forever
        client.check_msg()# Action a message if one is received. Non-blocking.
        send_random()     # Send a random number to Adafruit IO if it's time.
finally:                  # If an exception is thrown ...
    client.disconnect()   # ... disconnect the client and clean up.
    client = None
    wlan.disconnect()
    wlan = None
    pycom.rgbled(0x000022)# Status blue: stopped
    print("Disconnected from server and wlan")
