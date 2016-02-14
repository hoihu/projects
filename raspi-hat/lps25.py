"""
LPS25 - STMicro MEMS I2C pressure and temperature sensor driver for MicroPython

http://www.st.com/web/en/resource/technical/document/datasheet/DM00066332.pdf
see AN4450 application note for additional details of implementation

Supports floating point or fixed point return values

Example usage:
>>> from pyb import I2C
>>> from lps25 import LPS25
>>> lps = LPS25(I2C(1, I2C.MASTER), 0x5c)
>>> lps.read_pressure()
944.4485
>>> lps.read_temp()
21.71667
"""

from pyb import I2C
import pyb

class LPS25:    
    LPS_WHO_AM_I = const(0xf)
    LPS_PRESSURE_OUT = const(0x28)
    LPS_TEMP_OUT = const(0x2b)

    def __init__(self, i2c, address, fixed_point = False):
        """
        `fixed_point` makes this class use fixed point return values with 2 decimal places 
        (for hw without floating point support)
        """
        self.i2c = i2c
        self.address = address
        self.fixed_point = fixed_point
        self.start()
        
    def start(self):
        """ 
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
        """
        returns pressure in hPa (hPa*100 for fixed point)
        """
        data =  int.from_bytes(self.i2c.mem_read(3,self.address,LPS_PRESSURE_OUT | 0x80))
        if data & 0x80000000: data = data - 0xffffffff
        if self.fixed_point:
            return data * 25 // 1024
        else:
            return data / 4096
        
    def read_temp(self):
        """ return temperature in degrees celsius (celsius*100 for fixed point) """
        data = int.from_bytes(self.i2c.mem_read(2,self.address,LPS_TEMP_OUT | 0x80))
        if data & 0x8000: data = data - 0xffff
        if self.fixed_point:
            return 4250 + (data*10) // 48 
        else:
            return 42.5 + data/480
