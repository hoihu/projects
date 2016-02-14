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

class uSenseHAT:    
    I2C_ADDR_MATRIX = const(0x46)
    I2C_ADDR_TEMP_PRESSURE = const(0x5c)
    I2C_ADDR_HUMID_TEMP = const(0x5f)
    # XXX not yet supported is gyro - missing driver
    I2C_IMU = const(0x1c)
    I2C_IMU2 = const(0x6a)
    
    def __init__(self, i2c):
        self.i2c = i2c
        # init board sensors
        self.hts = HTS21(i2c, I2C_ADDR_HUMID_TEMP)
        self.lps = LPS25(i2c, I2C_ADDR_TEMP_PRESSURE)
        self.matrix = SenseAtmel(i2c ,I2C_ADDR_MATRIX)
        # xxx gyro not yet supported

    # convenience methods to ease access to sensors
    def read_key(self):
        return self.matrix.read_key()
        
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
            
                
