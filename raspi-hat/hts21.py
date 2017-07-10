"""
HTS221 - STMicro I2C temperature and humidity sensor driver for MicroPython

Example usage:
>>> from hts221 import HTS221
>>> hts = HTS221(I2C(1))
>>> hts.measure()
(30.8557, 62.07305)
"""
import array
import uctypes

class HTS221:    
    HTS_WHO_AM_I = const(0xf)
    
    def __init__(self, i2c, addr=95):
        self.i2c = i2c
        self.addr = addr
        if (self.i2c.readfrom_mem(addr, HTS_WHO_AM_I, 1) != b'\xbc'):
            raise OSError("No HTS221 device on address {} found".format(addr))
        self.cal_buf = bytearray(16)
        self.calib = uctypes.struct(uctypes.addressof(self.cal_buf), {
                'h0_rh':(uctypes.UINT8 | 0), 
                'h1_rh':(uctypes.UINT8 | 1), 
                't0_deg':(uctypes.UINT8 | 2), 
                't1_deg':(uctypes.UINT8 | 3), 
                'res':(uctypes.UINT8 | 4),
                't1t0msb':(uctypes.UINT8 | 5),
                'h0_out':(uctypes.INT16 | 6),
                'res1':(uctypes.INT16 | 8),
                'h1_out':(uctypes.INT16 | 10),
                't0_out':(uctypes.INT16 | 12),
                't1_out':(uctypes.INT16 | 14)})

        self.val_buf = bytearray(5)
        self.raw_val = uctypes.struct(uctypes.addressof(self.val_buf), {
                'status':(uctypes.UINT8 | 0), 
                'h_out':(uctypes.INT16 | 1), 
                't_out':(uctypes.INT16 | 3)})
        
        # enable sensor, one-shoot
        i2c.writeto_mem(addr, 0x20, b'\x84')
        i2c.readfrom_mem_into(95, 0x30|0x80, self.cal_buf)
        
        # add 2 bits from reg 0x35 -> 10bit unsigned values)
        self.t0_deg = (self.calib.t0_deg | ((self.calib.t1t0msb & 0x3) << 8))
        self.t1_deg = (self.calib.t1_deg | ((self.calib.t1t0msb & 0xc) << 6))
        
        self.t_slope = (self.t1_deg - self.t0_deg) / (self.calib.t1_out - self.calib.t0_out)
        self.h_slope = (self.calib.h1_rh - self.calib.h0_rh) / (self.calib.h1_out - self.calib.h0_out)
        
        print("h0_rh={}, h1_rh={}, h0_t0_out={}, h1_t0_out={}".format(
            self.calib.h0_rh, self.calib.h1_rh, self.calib.h0_out, self.calib.h1_out))
        print("t0_deg={}, t1_deg={}, t0_out={}, t1_out={}".format(
            self.t0_deg, self.t1_deg, self.calib.t0_out, self.calib.t1_out))
            
    def measure(self):
        # enable one-shot measurement
        self.i2c.writeto_mem(self.addr, 0x21, b'\x01')

    def measure_end(self):
        while(1):
            self.i2c.readfrom_mem_into(self.addr, 0x27 | 0x80, self.val_buf)
            if (self.raw_val.status & 0x3):
                break
            time.sleep_ms(10)

        self.temperature = (self.t0_deg + self.t_slope * (self.raw_val.t_out - self.calib.t0_out)) 
        self.humidity = (self.calib.h0_rh + self.h_slope * (self.raw_val.h_out - self.calib.h0_out)) 


    def config(self, heater=True):
        """ """
        if heater: 
            self.i2c.writeto_mem(self.addr, 0x21, b'\x02')
        else:
            self.i2c.writeto_mem(self.addr, 0x21, b'\x00')

    def get_humidity(self):
        """ """
        return self.humidity / 2.

    def get_humidity_fixed(self):
        """ """
        return (int(self.humidity) * 50) | (-2 + 128)

    def fixed_to_float(self,fx):
        return (fx >> 8) * 10**((fx & 0xff) - 128)

    def get_temperature(self):
        """ """
        return self.temperature / 8.

    def get_temperature_fixed(self):
        """ """
