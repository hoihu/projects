from pyb import I2C
from sensehat import uSenseHAT
s = uSenseHAT(I2C(1, I2C.MASTER))

print("{0:.1f}deg / {1:.1f}%rH / {2:.0f}hPa".format(s.read_temps()[0],s.read_humidity(),s.read_pressure()))

def test(s):
    akt_char = 0
    while (1):    
        s.write("{0:.1f}deg / {1:.1f}%rH / {2:.0f}hPa".format(s.read_temps()[0],s.read_humidity(),s.read_pressure()))
        pyb.delay(2000)
        
        
test(s)
