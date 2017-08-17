"""
LPS25 - STMicro I2C pressure/temperature sensor driver for MicroPython
>>> from lps25 import LPS25
>>> lps = LPS25(I2C(1))
>>> lps.measure()
>>> lps.get_temperature()
21.71667
"""
import uctypes
import time

class LPS25:    
    WHO_AM_I = const(0xf)

    def __init__(self, i2c, addr=92, fixed=False):
        self.i2c = i2c
        self.addr = addr
        self.fixed = fixed
        if (self.i2c.readfrom_mem(addr, WHO_AM_I, 1) != b'\xbd'):
            raise OSError("No LPS25 device on address {} found".format(addr))
        
        self.val_buf = bytearray(5)
        self.raw_val = uctypes.struct(uctypes.addressof(self.val_buf), { 
                'p_low':(uctypes.UINT8 | 0), 
                'p_out':(uctypes.UINT16 | 1), 
                't_out':(uctypes.INT16 | 3)})

        i2c.writeto_mem(addr, 0x20, b'\x00')
        i2c.writeto_mem(addr, 0x20, b'\x84')
    
    def measure(self):
        # init one-shot measurement
        self.i2c.writeto_mem(self.addr, 0x21, b'\x01')
        self.measure_done = False

    def measure_end(self):
        delay_cntr = 0
        while (delay_cntr < 10):
            if not (int.from_bytes(self.i2c.readfrom_mem(self.addr, 0x21, 1),'big') & 0x1):
                break
            time.sleep_ms(10)
            delay_cntr += 1
        else:
            raise OSError("Timeout Sensor")
        self.i2c.readfrom_mem_into(self.addr, 0x28|0x80, self.val_buf)
        # p_total is a signed 24 bit value...
        p_total = 256 * self.raw_val.p_out + self.raw_val.p_low
        if p_total & 0x800000: p_total -= 0xffffff
        if self.fixed:
            self.temperature = ((((20400 + self.raw_val.t_out) << 8) // 48 ) & ~0xff) | (-1 + 128)
            self.pressure = (((100 * p_total) >> 4) & ~0xff) | (-2 + 128)
        else:
            self.temperature = 42.5 + self.raw_val.t_out / 480
            self.pressure = p_total / 4096.

        self.measure_done = True

    def fixed_to_float(self,fx):
        # may be moved to a generic location
        return (fx >> 8) * 10**((fx & 0xff) - 128)

    def get_pressure(self):
        if not self.measure_done:
            self.measure_end()
        return self.pressure
            
    def get_temperature(self):
        if not self.measure_done:
            self.measure_end()
        return self.temperature
