"""
Implements basic support for SenseHAT board for MicroPython
details see https://www.raspberrypi.org/products/sense-hat/

                SenseHAT Board
                +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
                |                                                   |
I2c master  -------------> HTS21 (Humidity/Temp  @ addr 0x5f)       +
(RPi/Pyboard)   |  |                                                |
                +  |-----> LPS25H (Pressure/Temp @ addr 0x5c)       +
                |  |                                                |
                +  |-----> LSM9DS1 (9DOF IMU     @ addr 0x1c, 0x6a) +
                |  |                                                |
                +  |-----> 8x8 RGB LED Matrix &                     +
                |          Joystick Keys (Atmel  @ addr 0x46)       |
                +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

The class acts as a wrapper to simplify access to the 4 sensor IC's
Please see documentation of driver for detailed description

Example usage:
>>> from sensehat import uSenseHAT
>>> sense = uSenseHAT(I2C(1, I2C.MASTER))
>>> sense.matrix.write("Hi Micropython")   # scrolling text on LED matrix
>>> sense.matrix.set_pixel(4,4,(20,20,0))  # set pixel (4,4) to color (20,20,0)
>>> sense.humidity   # humidty in percent rH
58.25
>>> sense.temperature      # returns average temperature from HTS21 & LPS25 sensors
21.2213
>>> sense.pressure   # returns hPa
970.8609
>>> sense.key        # returns key state (pressed, left,right etc)
0
>>> sense.imu       # returns raw value of gyro, accelerometer, magnetometer
((-0.4037476, 0.8224488, -0.05233765), (-0.009338379, 0.07415771, 0.9942017), 
(0.5358887, -0.001586914, -0.1228027))

The values from gyro/accel/magnetometer can be used to calculate yaw/roll/pitch,
for example by using peter hinch's fusion module that implements the Madgwick algorithm
"""
import pyb
import array
from hts21 import HTS21
from lps25 import LPS25
from lsm9ds1 import LSM9DS1
from atmel import SenseAtmel

class uSenseHAT:    
    I2C_ADDR_MATRIX = const(0x46)
    I2C_ADDR_TEMP_PRESSURE = const(0x5c)
    I2C_ADDR_HUMID_TEMP = const(0x5f)
    
    def __init__(self, i2c):
        """ 
        a wrapper class that setups all sensors of a SenseHAT board
        and provides some easy helper properties
        """
        self.i2c = i2c
        # init drivers
        self.hts = HTS21(i2c, I2C_ADDR_HUMID_TEMP)
        self.lps = LPS25(i2c, I2C_ADDR_TEMP_PRESSURE)
        self.lsm = LSM9DS1(i2c)
        self.matrix = SenseAtmel(i2c ,I2C_ADDR_MATRIX)

    @property
    def key(self): 
        return self.matrix.key
        
    @property
    def pressure(self): 
        return self.lps.pressure
        
    @property
    def temperature(self):
        """ returns average temperature of hts21 and lps25 chip """
        return (self.hts.temperature + self.lps.temperature) / 2
        
    @property
    def humidity(self): 
        return self.hts.humidity
        
    @property
    def imu(self): 
        """ 
        returns 9DOF data: (gyro,accelerator,magnetometer) 
        containing (x,y,z) values scaled in deg/sec, g and gauss respecively
        """
        return (self.lsm.gyro, self.lsm.accel, self.lsm.magnet)
                
