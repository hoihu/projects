from pyb import I2C
import pyb
import array

# settings of I2C slaves of SenseHAT:
# Pressure/Temp: LPS25H -> 0x5c
# Humidity/Temp: HTS221 0x5f
# IMU (Gyroscope, Accelerometer, Magnetometer) 0x1c,0x6a
# LEDMatrix via ATTINY88: 0x46


I2C_ADDR_MATRIX = const(0x46)
I2C_ADDR_TEMP_PRESSURE = const(0x5c)
I2C_ADDR_HUMID_TEMP = const(0x5f)
I2C_IMU = const(0x1c)
I2C_IMU2 = const(0x6a)

# avail. registers for Atmel matrix
RPISENSE_FB    = const(0x00) 
RPISENSE_WAI   = const(0xF0) 
RPISENSE_VER   = const(0xF1) 
RPISENSE_KEYS  = const(0xF2) 
RPISENSE_EE_WP = const(0xF3)
RPISENSE_ID    = 's' 

# joystick values from register RPISENSE_KEYS
KEY_LEFT = const(0x10)
KEY_RIGHT = const(0x2)
KEY_TOP = const(0x4)
KEY_BOTTOM = const(0x1)
KEY_PRESS = const(0x8)

#avail registers for LPS25H (humidity/temp)
LPS_WHO_AM_I    = const(0xf)
LPS_REF_P       = const(8)
LPS_PRESSURE_OUT = const(0x28)
LPS_TEMP_OUT = const(0x2b)

# gamma table is taken from linux driver and limited to 31
# which is apparently set by the HW :/
# so the color range is limited to 32^3 = 32k Colours 
GAMMA_TABLE = array.array('B', [
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01, 
 	0x02, 0x02, 0x03, 0x03, 0x04, 0x05, 0x06, 0x07, 
 	0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0E, 0x0F, 0x11, 
 	0x12, 0x14, 0x15, 0x17, 0x19, 0x1B, 0x1D, 0x1F]
)

class ColorPixel:
    def __init__(self,r,g,b):
        self.set_colour(r,g,b)
        
    def set_colour(self,r,g,b):
        # make sure it's limited to 31 (according to linux driver..)
        # higher luminations may be possible, but I've observed inconsistent behaviour
        self.r = GAMMA_TABLE[r & 0x1F]
        self.g = GAMMA_TABLE[g & 0x1F]
        self.b = GAMMA_TABLE[b & 0x1F]

class uSenseHAT:    
    def __init__(self, i2c):
        self.i2c = i2c
        self.lps_init()
        self.vmem = array.array('B',[0 for  i in range(0,192)])
        
    def get_version(self):
        version = array.array('B',[0])
        self.i2c.mem_read(version, I2C_ADDR_MATRIX, RPISENSE_VER)
        print("HAT v.{}".format(version))
        
    def get_key(self):
        return self.i2c.mem_read(1, I2C_ADDR_MATRIX, RPISENSE_KEYS)
        
    def clear(self):
        self.vmem = array.array('B',[0 for  i in range(0,192)])
        self.refresh()
        
    def set_pixel(self, x, y, pixel, refresh=False):
        # sets one pixel in video buffer, using gamma correction
        self.vmem[24*y + x] = pixel.r
        self.vmem[24*y + x + 8] = pixel.g
        self.vmem[24*y + x + 16] = pixel.b
        if refresh:
            self.refresh()
         
    # -.-.-.-.-.-.-.-.-.-.- LPS functions (pressure & temperature)
    def lps_id(self):
        return self.i2c.mem_read(1,I2C_ADDR_TEMP_PRESSURE,LPS_WHO_AM_I)
        
    def lps_init(self):
        """ initialisation code for the LPS chip """
        # recommended init as of AN4450, 1Hz interval, 4uA
        self.i2c.mem_write(0x05,I2C_ADDR_TEMP_PRESSURE,0x10)
        self.i2c.mem_write(0xc1,I2C_ADDR_TEMP_PRESSURE,0x2e)
        self.i2c.mem_write(0x40,I2C_ADDR_TEMP_PRESSURE,0x21)
        self.i2c.mem_write(0x90,I2C_ADDR_TEMP_PRESSURE,0x20)
        
    def get_pressure(self):
        """ reads the pressure data and converts it to hPa"""
        data =  int.from_bytes(
            self.i2c.mem_read(1,I2C_ADDR_TEMP_PRESSURE,LPS_PRESSURE_OUT) + \
            self.i2c.mem_read(1,I2C_ADDR_TEMP_PRESSURE,LPS_PRESSURE_OUT+1) + \
            self.i2c.mem_read(1,I2C_ADDR_TEMP_PRESSURE,LPS_PRESSURE_OUT+2)
        )
        if data & 0x80000000:
            data = data - 0xffffffff
        return float("{0:.2f}".format(data /4096.))
        
    def get_temp(self):
        """ reads the temperature data and returns degrees celsius"""
        data = int.from_bytes(
            self.i2c.mem_read(1,I2C_ADDR_TEMP_PRESSURE,LPS_TEMP_OUT) + \
            self.i2c.mem_read(1,I2C_ADDR_TEMP_PRESSURE,LPS_TEMP_OUT+1)
        )
        if data & 0x8000:
            data = data - 0xffff
        return float("{0:.2f}".format(42.5 + data/480.))
        
    def refresh(self):
        """ refresh matrix data """
        self.i2c.mem_write(self.vmem,I2C_ADDR_MATRIX,0)
    
sense = uSenseHAT(I2C(1, I2C.MASTER))
        
def test():
    start = 1
    while (1):
        for x in range(8):
            for y in range(8):
                sense.set_pixel(x,y,ColorPixel((x + start) & 0xf,(y+start*2) & 0xf,0))
        sense.refresh()
        start +=1
        start = start & 0xff
        pyb.delay(200)
        
        
