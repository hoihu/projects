"""
HTS221 - STMicro I2C temperature and humidity sensor driver for MicroPython

Example usage:
>>> from hts221 import HTS221
>>> hts = HTS221(I2C(1))
>>> hts.measure()
(30.8557, 62.07305)
"""
import array
import struct

class HTS221:    
    HTS_WHO_AM_I = const(0xf)
    HTS_HUMID_OUT = const(0x28)
    HTS_TEMP_OUT = const(0x2a)
    
    def __init__(self, i2c, addr=95):
        self.i2c = i2c
        self.addr = addr
        if (self.i2c.readfrom_mem(addr, HTS_WHO_AM_I, 1) != b'\xbc'):
            raise OSError("No HTS221 device on address {} found".format(addr))

        # enable sensor and read calibration
        i2c.writeto_mem(addr, 0x20, b'\x85')
        self.h0_rh, h1_rh, self.t0_deg, t1_deg, res, t1t0msb, self.h0_out,res1, h1_out, self.t0_out, t1_out = struct.unpack('<BBBBBBhhhhh', i2c.readfrom_mem(95,0x30|0x80, 16))
        
        # add 2 bits from reg 0x35 -> 10bit unsigned values)
        self.t0_deg = (self.t0_deg | ((t1t0msb & 0x3) << 8)) >> 3
        t1_deg = (t1_deg | ((t1t0msb & 0xc) << 6)) >> 3
        
        self.t_slope = (t1_deg-self.t0_deg) / (t1_out-self.t0_out)
        self.h_slope = (h1_rh - self.h0_rh) / (h1_out - self.h0_out)
        
        print("h0_rh={}, h1_rh={}, h0_t0_out={}, h1_t0_out={}".format(
            self.h0_rh, h1_rh, self.h0_out, h1_out))
        print("t0_deg={}, t1_deg={}, t0_out={}, t1_out={}".format(
            self.t0_deg, t1_deg, self.t0_out, t1_out))
            
    def measure(self):
        """ returns (temp [deg], humidity [%rH]) """
        # see TN1218 appnote
        act_hout, act_tout = struct.unpack('<hh', self.i2c.readfrom_mem(self.addr, 0x28 | 0x80, 4))
        temp = self.t0_deg + self.t_slope * (act_tout - self.t0_out)
        humid = self.h0_rh + self.h_slope * (act_hout - self.h0_out)
        return temp,humid/2