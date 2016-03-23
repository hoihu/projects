

def clamp(n, minn, maxn): return min(max(n, minn), maxn)

class Balance:
    def __init__(self, matrix):
        """ a simple ball balancing example on the LED matrix"""
        self.v_x = 0
        self.v_y = 0
        self.pos_x = 4
        self.pos_y = 4
        self.matrix = matrix
        self.x_sum = 4
        self.y_sum = 4
        self.show(4,4)
        
    def clear(self):
        self.matrix.set_pixel(self.pos_x,self.pos_y,[0,0,0])
        
    def show(self,x1,y1):
        """ """
        distance = 0
        for x in range(0,8):
            for y in range(0,8):
                distance = (x-x1)**2 + (y-y1)**2 
                bright = int(clamp(31-distance**3,0,25))
                if bright>10:
                    self.matrix.set_pixel(x,y,(0, bright, 0))
                elif distance > 32:
                    self.matrix.set_pixel(x,y,(0,bright, 12))
                elif distance > 24:
                    self.matrix.set_pixel(x,y,(0,0, 5))
                else:
                    self.matrix.set_pixel(x,y,(0,0,0))
        self.matrix.refresh()
        
    def update(self, heading, pitch, roll):
        self.v_x += pitch / 600
        self.v_y -= roll / 600
        
        self.v_x = clamp(self.v_x, -0.7, 0.7)        
        self.v_y = clamp(self.v_y, -0.7, 0.7)        
        self.x_sum += self.v_x
        self.y_sum += self.v_y
                
        if (self.x_sum > 7) or (self.x_sum < 0):
            self.v_x = 0
        
        if (self.y_sum > 7) or (self.y_sum < 0):
            self.v_y = 0
        
        self.x_sum = clamp(self.x_sum, 0, 7)        
        self.y_sum = clamp(self.y_sum, 0, 7)        
        
        self.show(self.x_sum, self.y_sum)
        
        
