import pyb, machine
import limi
from writer import Writer

import myfont

limi.powerup()
display = limi.init_oled()

w = Writer(display.framebuf,myfont,width=160,height=128)
w.printstring("HEEYY")
# 
# display.pixel(1,1,1)
# display.pixel(140,1,1)
# display.pixel(140,127,1)
# def color_oled(r,g,b):
    
for r in range(0,255):
    display.framebuf.fill_rect(60,1,160,100, r << 13 )
    # display.fill_rect(60,1,160,100,r << 3 )
    # display.fill_rect(60,1,160,100,r << 8)
    w.printstring(str(r)+"\n")
    display.show()
    pyb.delay(100)
