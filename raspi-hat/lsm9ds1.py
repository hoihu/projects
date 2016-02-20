from pyb import I2C
import array

class LSM9DS1:
    #sensehat address gyro&accel = 106, magnetometer = 28
    WHO_AM_I = const(0xf)
    
    ACT_THS = const(4)
    ACT_DUR = const(5)
    
    INT_GEN_CDG = const(6)
        
    INT_GEN_THS = const(7)  # 3 bytes for x,y,z
    
    INT_GEN_DUR = const(0xa)
    REFERENCE_G = const(0xb)
    INT1_CTRL = const(0xc)
    INT2_CTRL = const(0xd)
    
    
    CTRL_REG1_G = const(0x10)
    CTRL_REG2_G = const(0x11)
    CTRL_REG3_G = const(0x12)
    
    ORIENT_CFG_G = const(0x13)
    INT_GEN_SRC_G = const(0x14)
    OUT_TEMP = const(0x15)  # 2 bytes
    OUT_G = const(0x18) # 6 bytes for x,y,z
    CTRL_REG4_G = const(0x1e)
    CTRL_REG5_XL = const(0x1f)
    CTRL_REG6_XL = const(0x20)
    CTRL_REG7_XL = const(0x21)
    CTRL_REG8 = const(0x22)
    CTRL_REG9 = const(0x23)
    CTRL_REG10 = const(0x24)
    
    STATUS_REG = const(0x27)
    OUT_XL = const(0x28)
    
    def __init__(self, i2c, address_gyro=106, address_magnet=28):
        self.i2c = i2c
        self.address_gyro = address_gyro
        self.address_magnet = address_magnet
        # check proper connections of accelerometer/gyro and magnetometer
        if ((i2c.mem_read(1, address_magnet, WHO_AM_I) != b'=') or \
           (i2c.mem_read(1, address_gyro, WHO_AM_I) != b'h')):
            raise OSError("No LSM9DS1 device")
        # ok - allocate scratch buffer for efficient conversions and memread op's
        self.scratch = array.array('B',[0,0,0,0,0,0])
        self.scratch_int = array.array('H',[0,0,0])
            
    def init_gyro_accel(self, sample_rate=1, scale_gyro=0, scale_accel=0, bw=0, low_power=0, hp_cutoff=0):
        """ 
        sample rate (gy&acc) = 0-6 (off, 14.9Hz, 59.5Hz, 119Hz, 238Hz, 476Hz, 952Hz)
        scale_gyro = 0,1,3 (245dps, 500dps, 2000dps )   (no 2!)
        scale_accel = 0-3 (+/-2g, +-16g, +/-4g, +/-8g)  (att. order!)
        bw = 0-3 (lowest-highest bandwith)
        hp_cutoff = 0-15 (lowest-highest highpass cutoff freq)
        """
        i2c = self.i2c
        addr = self.address_gyro
        i2c.mem_write(((sample_rate & 0x07) << 5) | ((scale_gyro & 0x3) << 3) | (bw & 0x3), addr, CTRL_REG1_G)
        i2c.mem_write(0x00, addr, CTRL_REG2_G)
        i2c.mem_write((low_power << 7) | (1 << 6) | (hp_cutoff & 0xf), addr, CTRL_REG3_G)
        # ctrl4 - enable x,y,z, outputs, no irq latching, no 4D
        i2c.mem_write(0x38, addr, CTRL_REG4_G) 
        i2c.mem_write(0x0, addr, ORIENT_CFG_G)
        # ctrl5, enable all axes
        i2c.mem_write(0x38, addr, CTRL_REG5_XL)
        # ctrl6, set scaling and sample rate of accel 
        i2c.mem_write(((sample_rate & 7) << 5) | ((scale_accel & 0x3) << 3) , addr, CTRL_REG6_XL) 
        
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
        self.i2c.mem_read(mv, self.address_gyro, OUT_XL | 0x80)
        return (mv[0],mv[1],mv[2])
        
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
         
    
        
        
            
            
        
            
        
