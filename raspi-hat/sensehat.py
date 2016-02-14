"""
SenseHAT support for MicroPython

Connect one of the two I2C busses to the SenseHAT board and 
use this class to access humidity, pressure, temperature, led matrix
and joystick values

Example usage:
"""

from pyb import I2C
import pyb
import array
from hts21 import HTS21
from lps25 import LPS25
from senseatmel import SenseAtmel
import font8x8vmsb as f

# settings of I2C slaves of SenseHAT:
# Pressure/Temp: LPS25H -> 0x5c
# Humidity/Temp: HTS221 -> 0x5f
# LED Matrix/Keys: ATTINY88 -> 0x46
# IMU (Gyroscope, Accelerometer, Magnetometer) -> 0x1c,0x6a

I2C_ADDR_MATRIX = const(0x46)
I2C_ADDR_TEMP_PRESSURE = const(0x5c)
I2C_ADDR_HUMID_TEMP = const(0x5f)
# XXX not yet supported is gyro - missing driver
I2C_IMU = const(0x1c)
I2C_IMU2 = const(0x6a)

class uSenseHAT:    
    def __init__(self, i2c):
        self.i2c = i2c
        # init board sensors
        self.hts = HTS21(i2c, I2C_ADDR_HUMID_TEMP)
        self.lps = LPS25(i2c, I2C_ADDR_TEMP_PRESSURE)
        self.matrix = SenseAtmel(i2c ,I2C_ADDR_MATRIX)
        # xxx gyro not yet supported

    # convenience methods to ease access to sensors
    def read_pressure(self):
        return self.lps.read_pressure()
    
    def read_temps(self):
        """ 
        returns temperatures of hts21 and lps25 chip
        """
        return (self.hts.read_temp(), self.lps.read_temp())
        
    def read_humidity(self):
        return self.hts.read_humidity()
        
    def putc_scroll(self,c):
        index = ord(c)
        m = self.matrix
        for x in range(8):
            data = f.font[index*8+x]
            for y in range(7,-1,-1):
                m.set_pixel(7,y,[(data & 0x1) * 10,0,0])
                data = data >> 1
            m.scroll(dir='left')
            m.refresh()
            pyb.delay(50)
        
    def putc(self,c):
        index = ord(c)
        m = self.matrix
        for x in range(8):
            data = f.font[index*8+x]
            for y in range(7,-1,-1):
                m.set_pixel(x,y,[(data & 0x1) * 10,0,0])
                data = data >> 1
        m.refresh()
        
    def write(self,text):
        m = self.matrix
        for c in text:
            self.putc_scroll(c)
            
                
def test(s):
    scroll_dir = 'up'
    akt_char = 0
    while (1):    
        s.write("HELLO WORLD!!")
        # s.putc(akt_char)
        # s.matrix.refresh()
        # pyb.delay(200)
        # while (not s.matrix.read_key()):
        #     pyb.delay(20)
        # for i in range(8):
        #     s.matrix.scroll(dir='left')
        #     s.matrix.refresh()
        #     pyb.delay(20)
        # akt_char += 1
        # if akt_char > 117: 
        #     akt_char = 0
        # for i in range(16):
        #     pyb.delay(20)
        #     if s.matrix.read_key() == s.matrix.KEY_UP:
        #         scroll_dir = 'up'
        #     elif s.matrix.read_key() == s.matrix.KEY_DOWN:
        #         scroll_dir = 'down'
        #     elif s.matrix.read_key() == s.matrix.KEY_LEFT:
        #         scroll_dir = 'left'
        #     elif s.matrix.read_key() == s.matrix.KEY_RIGHT:
        #         scroll_dir = 'right'
        #     s.matrix.scroll(dir=scroll_dir)
        #     if i>7:
        #         i=15-i
        #     if scroll_dir == 'up':
        #         s.matrix.set_pixel(i,7,[3,i*2+3,12])
        #     elif scroll_dir == 'down':
        #         s.matrix.set_pixel(i,0,[12,i*2+3,0])
        #     elif scroll_dir == 'left':
        #         s.matrix.set_pixel(7,i,[15,i*2+3,0])
        #     elif scroll_dir == 'right':
        #         s.matrix.set_pixel(0,i,[3,i*2+3,8])
        #     s.matrix.refresh()
            

s = uSenseHAT(I2C(1, I2C.MASTER))
test(s)
