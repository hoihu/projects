from pyb import I2C
import pyb
import array
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
KEY_TOP = const(0x4)
KEY_BOTTOM = const(0x1)
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
        """ refresh matrix data """
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
    start = 1
    while (1):
        for x in range(8):
            for y in range(8):
                s.set_pixel(x,y,[(x + start) & 0xf,(y+start*2) & 0xf,0])
        s.refresh()
        start +=1
        start = start & 0xff
        pyb.delay(100)
        
        
