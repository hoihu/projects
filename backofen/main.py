from pyb import Pin, ADC
import time
from ws2812 import WS2812

analog_pins = ['X2','X3','X4','X5','X1']
intensities = [0.8, 0.3, 0.1, 0.02, 0]
voltages = [4096, 2700, 1300, 0]

STANDBY_TIMEOUT = 300
SHUTDOWN_TIMEOUT = 400

LEDS_STANDBY = [
    (0,6,(0,255,0)),
    (6,7,(0,255,0)),
    (13,7,(0,255,0)),
    (20,7,(0,255,0)),
    (27,7,(0,255,0))]

LEDS_RED = [
    (0,6,(255,0,0)),
    (6,7,(255,0,0)),
    (13,7,(255,0,0)),
    (20,7,(255,0,0)),
    (27,7,(255,255,255))]

en = Pin('X11', Pin.OUT)

def shutdown():
    global lamps, en
    print("SHUTDOWN")
    for led in LEDS_RED:
        lamps.set_intensity(led,0)
    lamps.refresh()
    en.low()
    pyb.stop()

def update_leds(states, leds):
    global lamps
    for lamp_nr, state in enumerate(states):
        lamps.set_intensity(leds[lamp_nr], intensities[state])
    lamps.refresh()
    
def eval_state(counts):
    state = len(voltages)
    for voltage in voltages:
        if (counts > voltage-100) and (counts < voltage + 100):
            break
        state -= 1
    else:
        return None
    return state

class Lamps:
    def __init__(self, lamps):
        led_cnt = 0
        for lamp in lamps: 
            if led_cnt < lamp[0]+lamp[1]:
                led_cnt = lamp[0]+lamp[1]
        self.data = [(0,0,0) for i in range(0, led_cnt)]
        self.chain = WS2812(spi_bus=1, led_count=led_cnt)
        
    def set_intensity(self, lamp, intensity):
        for i in range(lamp[0], lamp[0]+lamp[1]):
            self.data[i] = (lamp[2][0]* intensity, lamp[2][1]* intensity, lamp[2][2]* intensity)
        
    def refresh(self):
        self.chain.show(self.data)

switches = [ADC(Pin(p)) for p in analog_pins]
lamps = Lamps(LEDS_RED)
lamps.set_intensity(LEDS_RED[0],0.5)
lamps.refresh()
time.sleep_ms(500)
en.high()
states = [0 for p in analog_pins]
time_last_changed = time.time()
standby_cntr = 1.1

while (True):
    measures = [sw.read() for sw in switches]
    # print("ADC counts = {}".format(measures))

    old_states = states
    states = [eval_state(count) for count in measures]
    
    for state in states:
        if state == None:
            # invalid (prelling) measurement, take last one
            states = old_states
            break
        
    for old, new in zip(old_states, states):
        if old != new:
            # state change, verify changes next time
            time_last_changed = time.time()
            continue
    
    if (time.time() - time_last_changed) > STANDBY_TIMEOUT:
        standby_cntr = standby_cntr ** 1.05
        if (standby_cntr > 10):
            standby_cntr = 1.1
        lamps.set_intensity(LEDS_STANDBY[0], (standby_cntr / 100.))
        lamps.refresh()

        if (time.time() - time_last_changed) > SHUTDOWN_TIMEOUT:
            shutdown()
        
    else:
        # normal operating mode, using red leds
        update_leds(states, LEDS_RED)
    # print("States = {}".format(states))
    time.sleep_ms(100)
