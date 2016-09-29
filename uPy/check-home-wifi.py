import network
import utime, time

import machine, neopixel
np = neopixel.NeoPixel(machine.Pin(4), 14)

WIFI_SSID_HOME = 'Fischernetz'

""" 
checks for a given home wifi network and shows on neopixel if it's available
connect neopixel on pin 4 (marked "SDA" on Huzzah board)
"""

def clear():
    for a in range(0,14):
        np[a] = [0,0,0]

def show1(on_state):
    if on_state:
        val = [12,0,0]
    else:
        val = [0,12,0]
        
    for i in range(0,14):
        clear()
        np[i] = val
        np.write()
        time.sleep_ms(25)
    

def check_home():
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    while(1):
        found = False
        ssids = sta_if.scan()
        for ssid in ssids:
            if ssid[0].decode('utf8') == WIFI_SSID_HOME:
                show1(True)
                found = True
                break
        if not found:
            show1(False)
            
        utime.sleep(5)

check_home()
