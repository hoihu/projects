import pyb, machine
import limi
from writer import Writer

import utime
import myfont


WIDTH = 160
HEIGHT = 128

NR_X = 10
NR_Y = 10

print("TEST")
WIDTH_RX= WIDTH // NR_X
HEIGHT_RY= HEIGHT // NR_Y

limi.powerup()
display = limi.init_oled()

print("HHH")
# w = Writer(display.framebuf,myfont,width=WIDTH,height=HEIGHT)
# w.printstring("HEEYY")

import gc
gc.collect() 

# start = utime.ticks_ms()
# print("starting: {}".format(start))
while(1):
        
    for i in range(0,100):
        for x in range(0,NR_X):
            for y in range(0,NR_Y):
                display.framebuf.fill_rect(
                    x* WIDTH_RX,
                    y* HEIGHT_RY,
                    WIDTH_RX - 3 ,
                    HEIGHT_RY - 3,
                    2+x*2+y*15+i*10)
                    # display.fill_rect(60,1,160,100,r << 3 )
                    # display.fill_rect(60,1,160,100,r << 8)
                    # w.printstring(str(r)+"\n")
                display.show()
                # pyb.delay(10)
                    
start = utime.ticks_ms()
print("starting: {}".format(start))

# for x in range(0,100):
#     display.framebuf.fill_rect(0,0,WIDTH, HEIGHT,0)
#     display.show()
#     display.framebuf.fill_rect(0,0,WIDTH, HEIGHT,7)
#     display.show()
    # pyb.delay(10)
    
    
for i in range(0,16):
    display.framebuf.scroll(10,0)
    display.show()
    
for i in range(0,12):
    display.framebuf.scroll(0,10)
    display.show()
    
print("finished in: {}".format(utime.ticks_ms()-start))
    
