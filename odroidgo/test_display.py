import time
import machine
from hw import tft

class BouncingBall:
    
    def __init__(self, tft, radius, color):
        self.tft = tft
        tft.clear()
        self.color = color
        self.radius = radius
        self.xmax = 320
        self.ymax = 240
        
    def start(self):
        vec_vel = [1,1]
        col = self.color
        xpos = ypos = self.radius
        shrink = 0.01
        while True:
            xmax = self.xmax - self.radius
            ymax = self.ymax - self.radius
            xmin = self.radius
            ymin = self.radius
            
            tft.circle(xpos, ypos, int(self.radius), 0)
            self.radius *= 1.0 + shrink
            xpos += vec_vel[0]
            ypos += vec_vel[1]
            tft.circle(xpos, ypos, int(self.radius), col)
            time.sleep_ms(10)
            if xpos > xmax: vec_vel[0] = -1
            elif ypos > ymax: vec_vel[1] = -1
            elif xpos < xmin: vec_vel[0] = 1
            elif ypos < ymin: vec_vel[1] = 1
            
            if self.radius > 30: 
                shrink = -0.01
            
            if self.radius < 10: 
                shrink = +0.01
            
        #~ tft.resetwin()
b = BouncingBall(hw.tft, 10, 0xff0000)
b.start()
