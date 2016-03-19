"""
LSM9DS1 - 9DOF inertial sensor of STMicro driver for MicroPython

The chip contains an accelerometer / gyroscope / magnetometer
The accelerometer/gyroscope and the magnetometer are using different I2C
addresses! The default addresses are valid for the SenseHAT board.

Example usage:
>>> from lsm9ds1 import LSM9DS1
>>> lsm = LSM9DS1(I2C(1, I2C.MASTER))
>>> lsm.gyro       # returns raw value of gyro sensor (x,y,z) in deg/sec
(-0.4037476, 0.8224488, -0.05233765)
>>> lsm.accel      # returns raw value of accel sensor (x,y,z) in g
(-0.009338379, 0.07415771, 0.9942017)
>>> lsm.magnet     # returns raw value of magnetometer (x,y,z) in gauss 
(0.5358887, -0.001586914, -0.1228027)
"""
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
    
    OFFSET_REG_X_M = const(0x05)
    CTRL_REG1_M = const(0x20)
    OUT_M = const(0x28)
    
    SCALE_GYRO = [(245,0),(500,1),(2000,3)]
    SCALE_ACCEL = [(2,0),(4,2),(8,3),(16,1)]
    
    def __init__(self, i2c, address_gyro=106, address_magnet=28):
        self.i2c = i2c
        self.address_gyro = address_gyro
        self.address_magnet = address_magnet
        # check id's of accelerometer/gyro and magnetometer
        if (self.id_magnet != b'=') or (self.id_gyro != b'h'):
            raise OSError("Invalid LSM9DS1 device, using address {}/{}".format(
                    address_gyro,address_magnet))
        # allocate scratch buffer for efficient conversions and memread op's
        self.scratch = array.array('B',[0,0,0,0,0,0])
        self.scratch_int = array.array('h',[0,0,0])
        self.init_gyro_accel()
        self.init_magnetometer()
        
    def init_gyro_accel(self, sample_rate=1, scale_gyro=0, scale_accel=0):
        """ 
        sample rate (gy&acc) = 0-6 (off, 14.9Hz, 59.5Hz, 119Hz, 238Hz, 476Hz, 952Hz)
        scale_gyro = 0-2 (245dps, 500dps, 2000dps ) 
        scale_accel = 0-3 (+/-2g, +/-4g, +/-8g, +-16g)
        """
        assert sample_rate <= 6, "invalid sampling rate: %d (0-6)" % sample_rate
        assert scale_gyro <= 2, "invalid scaling of gyro: %d (0-2)" % scale_gyro
        assert scale_accel <= 3, "invalid scaling of accelerometer: %d (0-3)" % scale_accel
        
        i2c = self.i2c
        addr = self.address_gyro
        # using memoryview and multibyte-write to speedup configuration
        mv = memoryview(self.scratch)        
        # anglular control registers 1-3 / Orientation
        mv[0] = ((sample_rate & 0x07) << 5) | ((self.SCALE_GYRO[scale_gyro][1] & 0x3) << 3) 
        mv[1:4] = b'\x00\x00\x00'
        i2c.mem_write(mv[:5], addr, CTRL_REG1_G)
        # ctrl4 - enable x,y,z, outputs, no irq latching, no 4D
        # ctrl5 - enable all axes, no decimation
        # ctrl6 - set scaling and sample rate of accel 
        # ctrl7,8 - leave at default values
        # ctrl9 - FIFO enabled
        mv[0] = mv[1] = 0x38
        mv[2] = ((sample_rate & 7) << 5) | ((self.SCALE_ACCEL[scale_accel][1] & 0x3) << 3)
        mv[3] = 0x00
        mv[4] = 0x4
        mv[5] = 0x2
        # we're using multibyte here without MSB set!
        # it seems to work whereas if MSB is set it doesn't..
        i2c.mem_write(mv[:6], addr, CTRL_REG4_G )
        self.reset_fifo()
        
        self.scale_factor_gyro = 32768 / self.SCALE_GYRO[scale_gyro][0]
        self.scale_factor_accel = 32768 / self.SCALE_ACCEL[scale_accel][0]
        
    def init_magnetometer(self, sample_rate=6, scale_magnet=0):
        """
        using high performance mode
        sample rates = 0-7 (0.625, 1.25, 2.5, 5, 10, 20, 40, 80Hz)
        scaling = 0-3 (+/-4, +/-8, +/-12, +/-16 Gauss)
        """
        assert sample_rate < 8, "invalid sample rate: %d (0-7)" % sample_rate
        assert scale_magnet < 4, "invalid scaling: %d (0-3)" % scale_magnet
        i2c = self.i2c
        addr = self.address_magnet
        mv = memoryview(self.scratch)       
        mv[0] = 0x40 | (sample_rate << 2) # ctrl1: sample rate, high performance mode
        mv[1] = scale_magnet << 5 # ctrl2: scale, normal mode, no reset
        mv[2] = 0x00 # ctrl3: continous conversion, no low power, I2C
        mv[3] = 0x08 # ctrl4: high performance z-axis
        mv[4] = 0x00 # ctr5: no fast read, no block update
        i2c.mem_write(mv[:5], addr, CTRL_REG1_M)
        self.scale_factor_magnet = 32768 / ((scale_magnet+1) * 4 )
        
    def write_magnet_calib(self, calibration):
        """ calibration is a tuple of (x,y,z) 16bit readings from sensor """
        mv = memoryview(self.scratch) 
        mv[0] = calibration[0] & 0xff
        mv[1] = calibration[0] >> 8
        mv[2] = calibration[1] & 0xff
        mv[3] = calibration[1] >> 8
        mv[4] = calibration[2] & 0xff
        mv[5] = calibration[2] >> 8
        self.i2c.mem_write(mv[:6], self.address_magnet, OFFSET_REG_X_M)
                
    @property
    def id_gyro(self):
        return self.i2c.mem_read(1, self.address_gyro, WHO_AM_I)
    
    @property
    def id_magnet(self):
        return self.i2c.mem_read(1, self.address_magnet, WHO_AM_I)
                        
    def read_raw(self, addr):
        return self.i2c.mem_read(1, self.address_gyro, addr)
        
    def write_raw(self, addr, data):
        self.i2c.mem_write(data, self.address_gyro, addr)
        
    @property
    def magnet(self, raw_values=False):
        """ """
        mv = memoryview(self.scratch_int)
        f = self.scale_factor_magnet
        self.i2c.mem_read(mv, self.address_magnet, OUT_M | 0x80)
        if raw_values:
            return (mv[0], mv[1], mv[2])
        else:
            return (mv[0]/f, mv[1]/f, mv[2]/f)
        # return (mv[0], mv[1], mv[2]),(mv[0]/f, mv[1]/f, mv[2]/f)
    
    @property
    def gyro(self):
        mv = memoryview(self.scratch_int)
        f = self.scale_factor_gyro
        self.i2c.mem_read(mv, self.address_gyro, OUT_G | 0x80)
        return (mv[0]/f, mv[1]/f, mv[2]/f)
    
    @property
    def accel(self):
        """ returns (x,y,z) acceleration vector in gravity units (9.81m/s^2) """
        mv = memoryview(self.scratch_int)
        f = self.scale_factor_accel
        self.i2c.mem_read(mv, self.address_gyro, OUT_XL | 0x80)
        return (mv[0]/f, mv[1]/f, mv[2]/f)
        
    def get_fifo(self):
        """ returns a sample of gyro and accelerometer if available """
        while(1):
            fifo_state = self.i2c.mem_read(1, self.address_gyro, FIFO_SRC)[0]
            if fifo_state & 0x3f:
                # print("Available samples=%d" % (fifo_state & 0x1f))
                yield self.read_gyro(),self.read_accel()
            else:
                break
        
    def reset_fifo(self):
        """ reset and enable fifo, using continous mode/overwrite old data if overflow"""
        self.i2c.mem_write(0x00, self.address_gyro, FIFO_CTRL_REG)
        self.i2c.mem_write(6 << 5, self.address_gyro, FIFO_CTRL_REG)
        
    def read_gyro_status(self):
        return self.i2c.mem_read(1, self.address_gyro, STATUS_REG)
        
    def set_orientation(self,x,y,z):
        """ flips orientation of x,y,z (Pitch,Roll,Yaw) """
        orientation = x << 5 | y << 4 | z << 3
        self.i2c.memwrite(orientation, self.address_gyro, ORIENT_CFG_G)
         
    
