from pyb import I2C
import array

class LSM9DS1:
    
    WHO_AM_I = const(0xf)
    CTRL_REG1_G = const(0x10)
    INT_GEN_SRC_G = const(0x14)
    OUT_TEMP = const(0x15)  # 2 bytes
    OUT_G = const(0x18) # 6 bytes for x,y,z
    CTRL_REG4_G = const(0x1e)
    
    STATUS_REG = const(0x27)
    OUT_XL = const(0x28)
    FIFO_CTRL_REG = const(0x2e)
    FIFO_SRC = const(0x2f)
    #sensehat address gyro&accel = 106, magnetometer = 28
    def __init__(self, i2c, address_gyro=106, address_magnet=28):
        self.i2c = i2c
        self.address_gyro = address_gyro
        self.address_magnet = address_magnet
        # check proper connections of accelerometer/gyro and magnetometer
        if ((i2c.mem_read(1, address_magnet, WHO_AM_I) != b'=') or \
           (i2c.mem_read(1, address_gyro, WHO_AM_I) != b'h')):
            raise OSError("No LSM9DS1 device")
        # allocate scratch buffer for efficient conversions and memread op's
        self.scratch = array.array('B',[0,0,0,0,0,0])
        self.scratch_int = array.array('h',[0,0,0])
        
    def init_gyro_accel(self, sample_rate=1, scale_gyro=0, scale_accel=0):
        """ 
        sample rate (gy&acc) = 0-6 (off, 14.9Hz, 59.5Hz, 119Hz, 238Hz, 476Hz, 952Hz)
        scale_gyro = 0-2 (245dps, 500dps, 2000dps ) 
        scale_accel = 0-3 (+/-2g, +/-4g, +/-8g, +-16g)
        """
        i2c = self.i2c
        addr = self.address_gyro
        # we are needing scaling factors for conversion results
        self.scale_gyro = scale_gyro
        self.scale_accel = scale_accel
        # using memoryview and multibyte-write to speedup configuration
        mv = memoryview(self.scratch)
        # anglular control registers 1-3 / Orientation
        # patch scaling according to register definitions
        # accelerator mapping (0->0 1->2 2->3 3->1)
        reg_scale_gyro = scale_gyro
        if scale_gyro >= 2: 
            reg_scale_gyro = 3
            
        reg_scale_accel = 0
        if scale_accel >= 3:
            reg_scale_accel = 1
        elif scale_accel:
            reg_scale_accel = scale_accel + 1
            
        mv[0] = ((sample_rate & 0x07) << 5) | ((reg_scale_gyro & 0x3) << 3) 
        mv[1:4] = b'\x00\x00\x00'
        i2c.mem_write(mv[:5], addr, CTRL_REG1_G)
        # ctrl4 - enable x,y,z, outputs, no irq latching, no 4D
        # ctrl5 - enable all axes, no decimation
        # ctrl6 - set scaling and sample rate of accel 
        # ctrl7,8 - leave at default values
        # ctrl9 - FIFO enabled
        mv[0] = mv[1] = 0x38
        mv[2] = ((sample_rate & 7) << 5) | ((reg_scale_accel & 0x3) << 3)
        mv[3] = 0x00
        mv[4] = 0x4
        mv[5] = 0x2
        # we're using multibyte here without MSB set!
        # it seems to work whereas if MSB is set it doesn't..
        i2c.mem_write(mv[:6], addr, CTRL_REG4_G )
        self.reset_fifo()
        
    def read_raw(self,addr):
        return self.i2c.mem_read(1, self.address_gyro, addr)
        
    def write_raw(self,addr,data):
        self.i2c.mem_write(data, self.address_gyro, addr)
        
    def read_gyro(self):
        mv = memoryview(self.scratch_int)
        self.i2c.mem_read(mv, self.address_gyro, OUT_G | 0x80)
        return (mv[0],mv[1],mv[2])
        
    def read_accel(self):
        mv = memoryview(self.scratch_int)
        scale = 32768 / (1 << (self.scale_accel+1))
        self.i2c.mem_read(mv, self.address_gyro, OUT_XL | 0x80)
        return (mv[0] / scale,mv[1] / scale, mv[2] / scale)
        
    def read_fifo_state(self):
        """ returns overflow condition and unread samples as tuple """
        tmp = self.i2c.mem_read(1, self.address_gyro, FIFO_SRC)
        return ((tmp[0] >> 6) & 1, (tmp[0] & 0x1f ))
        
    def reset_fifo(self):
        """ reset and enable fifo, using continous mode, overwrite old data if overflow"""
        self.i2c.mem_write(0x00, self.address_gyro, FIFO_CTRL_REG)
        self.i2c.mem_write(6 << 5, self.address_gyro, FIFO_CTRL_REG)
        
    def read_gyro_status(self):
        return self.i2c.mem_read(1, self.address_gyro, STATUS_REG)
        
    def init_magnet(self,sample_rate=1, scale=0):
        """
        """
        mv = memoryview(self.scratch)
        
    def set_orientation(self,x,y,z):
        """ flips orientation of x,y,z (Pitch,Roll,Yaw) """
        orientation = x << 5 | y << 4 | z << 3
        self.i2c.memwrite(orientation, self.address_gyro, ORIENT_CFG_G)
         
    
