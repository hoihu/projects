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
from profile import *
from hts21 import HTS21
from lps25 import LPS25

# settings of I2C slaves of SenseHAT:
# Pressure/Temp: LPS25H -> 0x5c
# Humidity/Temp: HTS221 0x5f
# IMU (Gyroscope, Accelerometer, Magnetometer) 0x1c,0x6a
# LEDMatrix: ATTINY88 0x46

I2C_ADDR_MATRIX = const(0x46)
I2C_ADDR_TEMP_PRESSURE = const(0x5c)
I2C_ADDR_HUMID_TEMP = const(0x5f)
# XXX not yet supported is gyro - missing driver
I2C_IMU = const(0x1c)
I2C_IMU2 = const(0x6a)

# avail. registers for Atmel matrix
RPISENSE_FB    = const(0x00) 
RPISENSE_WAI   = const(0xF0) 
RPISENSE_VER   = const(0xF1) 
RPISENSE_KEYS  = const(0xF2) 
RPISENSE_EE_WP = const(0xF3)
RPISENSE_ID    = 's' 

# joystick values from register RPISENSE_KEYS
KEY_LEFT = const(0x10)
KEY_RIGHT = const(0x2)
KEY_UP = const(0x4)
KEY_DOWN = const(0x1)
KEY_PRESS = const(0x8)

# gamma table is taken from linux driver and limited to 31
# which is apparently set by the HW :/
# so the color range is limited to 32^3 = 32k Colours 
# XXX some values are suspicious (e.g. 0x12 -> 0x14 -> 0x15)
#     that it's not logarithmic...
GAMMA_TABLE = array.array('B', [
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01, 
 	0x02, 0x02, 0x03, 0x03, 0x04, 0x05, 0x06, 0x07, 
 	0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0E, 0x0F, 0x11, 
 	0x12, 0x14, 0x15, 0x17, 0x19, 0x1B, 0x1D, 0x1F]
)

class uSenseHAT:    
    def __init__(self, i2c):
        self.i2c = i2c
        # init board sensors
        self.hts = HTS21(i2c,I2C_ADDR_HUMID_TEMP)
        self.lps = LPS25(i2c,I2C_ADDR_TEMP_PRESSURE)
        # xxx gyro not yet supported
        # buffer for LED data
        self.vmem = array.array('B',[0 for  i in range(0,192)])
        self.vmem_mv = memoryview(self.vmem)
        
    def read_key(self):
        """ 
        returns onboard joystick state 
        valid return values are KEY_xxx values (0,1,2,4,8,16)
        """
        return int.from_bytes(self.i2c.mem_read(1, I2C_ADDR_MATRIX, RPISENSE_KEYS))
        
    def clear(self):
        """ clears LED matrix """
        self.vmem = array.array('B',[0 for  i in range(0,192)])
        self.refresh()
        
    def scroll_vertical(self, dir = 'up'):
        """ scrolls matrix vertically (up or down), ca. 1.5msec """
        vmem = self.vmem_mv
        if dir == 'up':
            for x in range(8):
                for y in range(0,7):
                    newpos = 24*y+x
                    oldpos = 24*(y+1)+x
                    vmem[newpos] = vmem[oldpos]
                    vmem[newpos+8] = vmem[oldpos+8]
                    vmem[newpos+16] = vmem[oldpos+16]
            for x in range(8): 
                vmem[168+x] = 0
                vmem[176+x] = 0
                vmem[184+x] = 0
                
        elif dir == 'down': 
            for x in range(8):
                for y in range(7,0,-1):
                    newpos = 24*y+x
                    oldpos = 24*(y-1)+x
                    vmem[newpos] = vmem[oldpos]
                    vmem[newpos+8] = vmem[oldpos+8]
                    vmem[newpos+16] = vmem[oldpos+16]
            for x in range(8):
                vmem[x] = 0
                vmem[x+8] = 0
                vmem[x+16] = 0
                
        elif dir == 'left':
            for y in range(8):
                for x in range(0,7):
                    newpos = 24*y+x
                    oldpos = 24*y+x+1
                    vmem[newpos] = vmem[oldpos]
                    vmem[newpos+8] = vmem[oldpos+8]
                    vmem[newpos+16] = vmem[oldpos+16]
            for y in range(8): 
                vmem[24*y+7] = 0
                vmem[24*y+15] = 0
                vmem[24*y+23] = 0    
        
        elif dir == 'right':
            for y in range(8):
                for x in range(7,0,-1):
                    newpos = 24*y+x
                    oldpos = 24*y+x-1
                    vmem[newpos] = vmem[oldpos]
                    vmem[newpos+8] = vmem[oldpos+8]
                    vmem[newpos+16] = vmem[oldpos+16]
            for y in range(8): 
                vmem[24*y] = 0
                vmem[24*y+8] = 0
                vmem[24*y+16] = 0    
                
        
    def set_pixel(self, x, y, color, refresh=False):
        """ 
        sets one pixel in video buffer, using gamma correction
        color is a list of [r,g,b] value and is limited to 0..31
        which is a HW limitation of the sensehat
        """
        self.vmem[24*y+x] = GAMMA_TABLE[color[0] & 0x1F]
        self.vmem[24*y+x+8] = GAMMA_TABLE[color[1] & 0x1F]
        self.vmem[24*y+x+16] = GAMMA_TABLE[color[2] & 0x1F]
        if refresh: self.refresh()

    def refresh(self):
        """ refresh matrix data, takes ca.5msec  """
        self.i2c.mem_write(self.vmem,I2C_ADDR_MATRIX,0)

    # convenience methods to ease access to sensors
    def read_pressure(self):
        return self.lps.read_pressure()
    
    def read_temps(self):
        """ returns temperature of hts21 and lps25 chip"""
        return (self.hts.read_temp(), self.lps.read_temp())
        
    def read_humidity(self):
        return self.hts.read_humidity()
        
s = uSenseHAT(I2C(1, I2C.MASTER))
        
def test():
    scroll_dir = 'up'
    while (1):    
        for i in range(16):
            pyb.delay(20)
            line = []
            s.scroll_vertical(dir=scroll_dir)
            if i>7:
                i=15-i
            if scroll_dir == 'up':
                s.set_pixel(i,7,[0,i*2+3,8])
            elif scroll_dir == 'down':
                s.set_pixel(i,0,[12,i*2+3,0])
            elif scroll_dir == 'left':
                s.set_pixel(7,i,[12,i*2+3,0])
            elif scroll_dir == 'right':
                s.set_pixel(0,i,[0,i*2+3,8])
                            
            s.refresh()
            if s.read_key() == KEY_UP:
                scroll_dir = 'up'
            elif s.read_key() == KEY_DOWN:
                scroll_dir = 'down'
            elif s.read_key() == KEY_LEFT:
                scroll_dir = 'left'
            elif s.read_key() == KEY_RIGHT:
                scroll_dir = 'right'
                            
