import network, utime

start_time = utime.ticks_ms()

SSID = YOUR_SSID
WIFI_PW = YOUR_PW

# ----------------------------------------------------------
# Define callback function used for monitoring wifi activity
# ----------------------------------------------------------
def wifi_cb(info):
    if (info[2]):
        msg = ", info: {}".format(info[2])
    else:
        msg = ""
    print("{} [WiFi] event: {} ({}){}".format(utime.ticks_diff(utime.ticks_ms(), start_time), info[0], info[1], msg))

# Enable callbacks
network.WLANcallback(wifi_cb)

# Test WIFI
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(SSID, WIFI_PW)
tmo = 50
while not sta_if.isconnected():
    utime.sleep_ms(100)
    tmo -= 1
    if tmo == 0:
        break
print("Connected to WIFI")
sta_if.ifconfig()

# test MDNS
try:
    mdns = network.mDNS()
    mdns.start("mPy","MicroPython with mDNS")
    _ = mdns.addService('_ftp', '_tcp', 21, "MicroPython", {"board": "ESP32", "service": "mPy FTP File transfer", "passive": "True"})
    _ = mdns.addService('_telnet', '_tcp', 23, "MicroPython", {"board": "ESP32", "service": "mPy Telnet REPL"})
    _ = mdns.addService('_http', '_tcp', 80, "MicroPython", {"board": "ESP32", "service": "mPy Web server"})
except:
    print("mDNS not started")
    
# now you can ping, e.g. "ping mpy.local" from your shell
    