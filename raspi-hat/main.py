from machine import I2C
import pyb
from sensehat import uSenseHAT
s = uSenseHAT(I2C(1))

def test(s):
    """ displays a scrolling text with temperature, pressure, humidity information"""
    while (1):    
        s.measure()
        s.matrix.write("{0:.1f}deg / {1:.1f}%rH / {2:.0f}hPa".format(
                s.get_temperature(), s.get_humidity(),s.get_pressure()))
        pyb.delay(2000)
        
test(s)


#import pyb
#from machine import I2C
#from balancing import Balance
#from fusion import Fusion
#from sensehat import uSenseHAT
#
#s = uSenseHAT(I2C(1))
#fuse = Fusion()
#balance = Balance(s.matrix)
#
#while (1):
#    for g,a in s.lsm.iter_accel_gyro():
#        fuse.update(a, g, s.lsm.read_magnet())
#        balance.update(fuse.heading, fuse.pitch, fuse.roll)
#    pyb.delay(5)
