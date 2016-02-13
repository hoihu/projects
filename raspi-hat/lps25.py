"""
LPS25 - ST MEMS I2C pressure and temperature sensor driver for MicroPython

http://www.st.com/web/en/resource/technical/document/datasheet/DM00066332.pdf
see AN4450 application note for additional details of implementation

Is part of the SenseHAT board

Example usage:
>>> from pyb import I2C
>>> from lps25 import LPS25
>>> lps = LPS25(I2C(1, I2C.MASTER), 0x5c)
>>> lps.read_pressure()
944.4485
>>> lps.read_temp()
21.71667
"""

LPS_WHO_AM_I = const(0xf)
LPS_PRESSURE_OUT = const(0x28)
LPS_TEMP_OUT = const(0x2b)

from pyb import I2C
import pyb

class LPS25:    
    def __init__(self, i2c, address):
        self.i2c = i2c
        self.address = address
        self.init()
        
    def init(self):
        """ 
        initialisation code
        recommended init as of AN4450, 1Hz interval, 4uA avg current consumption
        """
        adr = self.address 
        i2c = self.i2c
        i2c.mem_write(0x05,adr,0x10)
        i2c.mem_write(0xc1,adr,0x2e)
        i2c.mem_write(0x40,adr,0x21)
        i2c.mem_write(0x90,adr,0x20)
        
    def read_id(self):
        return self.i2c.mem_read(1,self.address,LPS_WHO_AM_I)
    
    def read_pressure(self):
        """ return pressure in hPa"""
        data =  int.from_bytes(self.i2c.mem_read(3,self.address,LPS_PRESSURE_OUT | 0x80))
        if data & 0x80000000: data = data - 0xffffffff
        return data / 4096
        
    def read_temp(self):
        """ read temperature in degrees celsius"""
        data = int.from_bytes(self.i2c.mem_read(2,self.address,LPS_TEMP_OUT | 0x80))
        if data & 0x8000: data = data - 0xffff
        return 42.5 + data/480
