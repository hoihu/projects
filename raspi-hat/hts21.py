"""
HTS21 - I2C temperature and humidity sensor driver for MicroPython
Part of SenseHAT board for the raspberry pi

Example usage:
>>> from pyb import I2C
>>> from hts21 import HTS21
>>> hts = HTS21(I2C(1, I2C.MASTER), 0x5f)
>>> hts.read_temperature()
22.06582
>>> hts.read_humidity()
57.44328
"""
from pyb import I2C
import pyb
import array

HTS_HUMID_OUT = const(0x28)
HTS_CAL_H0x2 = const(0x30)
HTS_CAL_H1x2 = const(0x31)
HTS_CAL_H0T0 = const(0x36)
HTS_CAL_H1T0 = const(0x3a)

HTS_TEMP_OUT = const(0x2a)
HTS_CAL_T0DEGx8 = const(0x32)
HTS_CAL_T1DEGx8 = const(0x33)
HTS_CAL_T0 = const(0x3c)
HTS_CAL_T1 = const(0x3e)

class HTS21:    
    def __init__(self, i2c, address):
        self.i2c = i2c
        self.address = address
        self.hts_calib = array.array("h",[0,0,0,0,0,0,0,0,0,0])
        self.init()

    def init(self):
        # see TN1218 appnote for details
        # read humidity calibration values
        # using memoryview here to optimize RAM usage, using i2c as shortcut
        # speed is limited by I2c bus: 2Bytes memread = ca.120usec @ 400kHz
        # and 37usec between the memread calls = ca.1.4msec total for init
        i2c = self.i2c
        adr = self.address
        mv = memoryview(self.hts_calib)
        # init measurement mode, enable sensor
        i2c.mem_write(0x81,adr,0x20)
        # read temperature calibration values
        # we are converting everything as signed as 0,1 values are limited to 10bits
        # and 5,6 are right shifted, thus MSB is always 0
        mv[0] = int.from_bytes(i2c.mem_read(1,adr,HTS_CAL_T0DEGx8))
        mv[1] = int.from_bytes(i2c.mem_read(1,adr,HTS_CAL_T1DEGx8))
        mv[2] = int.from_bytes(i2c.mem_read(2,adr,HTS_CAL_T0 | 0x80))
        mv[3] = int.from_bytes(i2c.mem_read(2,adr,HTS_CAL_T1 | 0x80))
        msbs = int.from_bytes(i2c.mem_read(1,adr, 0x35))
        mv[0] = (mv[0] | ((msbs & 0x3) << 8)) >> 3
        mv[1] = (mv[1] | ((msbs & 0xc) << 6)) >> 3
        # read humidity values
        mv[5] = int.from_bytes(i2c.mem_read(1,adr,HTS_CAL_H0x2)) >> 1
        mv[6] = int.from_bytes(i2c.mem_read(1,adr,HTS_CAL_H1x2)) >> 1
        mv[7] = int.from_bytes(i2c.mem_read(2,adr,HTS_CAL_H0T0 | 0x80))
        mv[8] = int.from_bytes(i2c.mem_read(2,adr,HTS_CAL_H1T0 | 0x80))

    def read_humidity(self):
        """ returns humidity in %rH"""
        # see TN1218 appnote for details about the formula
        mv = memoryview(self.hts_calib)   
        mv[9] = int.from_bytes(self.i2c.mem_read(2,self.address,HTS_HUMID_OUT | 0x80))
        return mv[5] + ((mv[6] - mv[5]) * (mv[9] - mv[7])) / (mv[8] - mv[7])
        
    def read_temp(self):
        """ returns temperature in degree celsius"""
        # see TN1218 appnote for details
        mv = memoryview(self.hts_calib)   
        mv[4] = int.from_bytes(self.i2c.mem_read(2,self.address,HTS_TEMP_OUT | 0x80))
        return mv[0] + ((mv[1] - mv[0]) * (mv[4] - mv[2])) / (mv[3] - mv[2])
        
h = HTS21(I2C(1, I2C.MASTER),0x5f)
