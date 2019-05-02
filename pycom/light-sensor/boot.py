# boot.py -- run on boot-up
from network import WLAN      # For operation of WiFi network
import time                   # Allows use of time.sleep() for delays

# Wireless network
WIFI_SSID = "DarthGuest"
WIFI_PASS = ""

# WIFI
wlan = WLAN(mode=WLAN.STA)
wlan.connect(WIFI_SSID, timeout=5000)
time.sleep(3)

while not wlan.isconnected(): # Code waits here until WiFi connects
    machine.idle()

print("Connected to Wifi")
