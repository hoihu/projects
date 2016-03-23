# from pyb import I2C
# import pyb
# from sensehat import uSenseHAT
# s = uSenseHAT(I2C(1, I2C.MASTER))
# 
# def test(s):
#     """ displays a scrolling text with temperature, pressure, humidity information"""
#     while (1):    
#         s.matrix.write("{0:.1f}deg / {1:.1f}%rH / {2:.0f}hPa".format(
#             s.temperature, s.humidity,s.pressure))
#         pyb.delay(2000)
#         
# test(s)


import pyb
from pyb import I2C
from balancing import Balance
import json as j

from fusion import Fusion

i2c = I2C(1, I2C.MASTER)
i2c.deinit()
i2c.init(I2C.MASTER)

from sensehat import uSenseHAT
s = uSenseHAT(i2c)
fuse = Fusion()
balance = Balance(s.matrix)

while (1):
    fuse.update(s.lsm.accel, s.lsm.gyro, s.lsm.magnet)
    balance.update(fuse.heading, fuse.pitch, fuse.roll)
    pyb.delay(5)
