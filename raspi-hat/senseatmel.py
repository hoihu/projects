"""
Driver for Atmel Coprocessor on SenseHAT board.

The Atmel controls the LED driver chip and reads the key states. It's connected
by I2C to the master device (normally a raspbery pi) and emulates a I2C memory

The gamma correction must be implemented at the driver side. It is taken
from the Linux driver and is limited to 31 - seems to be a HW limitation. 
"""

from pyb import I2C
import pyb
import array

class SenseAtmel:
    RPISENSE_FB = const(0x00)
    RPISENSE_VER = const(0xF1)
    RPISENSE_KEYS = const(0xF2)
    RPISENSE_ID = 's' 

    # joystick values from register RPISENSE_KEYS
    KEY_LEFT = const(0x10)
    KEY_RIGHT = const(0x2)
    KEY_UP = const(0x4)
    KEY_DOWN = const(0x1)
    KEY_PRESS = const(0x8)

    # gamma table is taken from linux driver and limited to 31
    # which is apparently set by the HW :/
    # so the color range is limited to 32^3 = 32k Colours 
    # XXX some values are suspicious (e.g. 0x12 -> 0x14 -> 0x15)
    #     that it's not logarithmic...
    GAMMA_NORMAL = array.array('B', [
        0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x01, 0x01, 
 	    0x02, 0x02, 0x03, 0x03, 0x04, 0x04, 0x05, 0x06, 
 	    0x07, 0x08, 0x0A, 0x0B, 0x0C, 0x0E, 0x0F, 0x11, 
 	    0x12, 0x14, 0x15, 0x17, 0x19, 0x1B, 0x1D, 0x1F]
    )
    
    GAMMA_LOW_LIGHT = array.array('B', [
        0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 
        3, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 10, 10]
    )
    
    def __init__(self, i2c, address):
        self.i2c = i2c
        self.address = address
        self.gamma = self.GAMMA_NORMAL
        # buffer for LED data
        self.vmem = array.array('B',[0 for  i in range(0,192)])
        self.vmem_mv = memoryview(self.vmem)
        
    def read_key(self):
        """ 
        returns onboard joystick state 
        valid return values are KEY_xxx integer values
        """
        return int.from_bytes(self.i2c.mem_read(1, self.address, RPISENSE_KEYS))
        
    def clear(self):
        """ 
        clears LED matrix 
        """
        self.vmem = array.array('B',[0 for  i in range(0,192)])
        self.refresh()
        
    def scroll(self, dir = 'up'):
        """ 
        scrolls matrix in the given direction and empties the scrolled line
        takes ca. 1.5msec 
        """
        vmem = self.vmem_mv
        if dir == 'up':
            for x in range(8):
                for y in range(0,7):
                    newpos = 24*y+x
                    oldpos = 24*(y+1)+x
                    vmem[newpos] = vmem[oldpos]
                    vmem[newpos+8] = vmem[oldpos+8]
                    vmem[newpos+16] = vmem[oldpos+16]
            for x in range(8): 
                vmem[168+x] = 0
                vmem[176+x] = 0
                vmem[184+x] = 0
                
        elif dir == 'down': 
            for x in range(8):
                for y in range(7,0,-1):
                    newpos = 24*y+x
                    oldpos = 24*(y-1)+x
                    vmem[newpos] = vmem[oldpos]
                    vmem[newpos+8] = vmem[oldpos+8]
                    vmem[newpos+16] = vmem[oldpos+16]
            for x in range(8):
                vmem[x] = 0
                vmem[x+8] = 0
                vmem[x+16] = 0
                
        elif dir == 'left':
            for y in range(8):
                for x in range(0,7):
                    newpos = 24*y+x
                    oldpos = 24*y+x+1
                    vmem[newpos] = vmem[oldpos]
                    vmem[newpos+8] = vmem[oldpos+8]
                    vmem[newpos+16] = vmem[oldpos+16]
            for y in range(8): 
                vmem[24*y+7] = 0
                vmem[24*y+15] = 0
                vmem[24*y+23] = 0    
        
        elif dir == 'right':
            for y in range(8):
                for x in range(7,0,-1):
                    newpos = 24*y+x
                    oldpos = 24*y+x-1
                    vmem[newpos] = vmem[oldpos]
                    vmem[newpos+8] = vmem[oldpos+8]
                    vmem[newpos+16] = vmem[oldpos+16]
            for y in range(8): 
                vmem[24*y] = 0
                vmem[24*y+8] = 0
                vmem[24*y+16] = 0    
                
    def set_low_light(self):
        self.gamma = self.GAMMA_LOW_LIGHT
    
    def set_normal_light(self):
        self.gamma = self.GAMMA_NORMAL
    
    def set_pixel(self, x, y, color, refresh=False):
        """ 
        sets one pixel in video buffer, using gamma correction
        color is a list of [r,g,b] values and is limited to 0..31
        which is a HW limitation of the sensehat
        """
        self.vmem[24*y+x] = self.gamma[color[0] & 0x1F]
        self.vmem[24*y+x+8] = self.gamma[color[1] & 0x1F]
        self.vmem[24*y+x+16] = self.gamma[color[2] & 0x1F]
        if refresh: self.refresh()

    def refresh(self):
        """ 
        refresh matrix data
        takes ca.5msec  
        """
        self.i2c.mem_write(self.vmem,self.address,0)
            
