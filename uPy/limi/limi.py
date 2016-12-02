import pyb, machine

led_red = machine.Pin('PC3',pyb.Pin.OUT_PP)
led_red.low()

def powerup():
    # power up system
    buck_en = machine.Pin('PB6',pyb.Pin.OUT_PP)
    ldo_en = machine.Pin('PC2',pyb.Pin.OUT_PP)
    hwpr = machine.Pin('PD2',pyb.Pin.OUT_PP)

    ldo_en.high()
    buck_en.high()
    hwpr.high()
    pyb.delay(100)

    boost_en = machine.Pin('PC0',pyb.Pin.OUT_PP)
    boost_en.high()
    pyb.delay(100)
 
def init_oled():
    # init oled
    import seps525
    spi1 = pyb.SPI(1,pyb.SPI.MASTER,baudrate=30000000)
    oled_rs = machine.Pin('PC4',pyb.Pin.OUT_PP)
    oled_cs = machine.Pin('PC5',pyb.Pin.OUT_PP)
    oled_nrst = machine.Pin('PB1',pyb.Pin.OUT_PP)
    oled_nrst.low()
    oled_rs.high()
    oled_cs.high()
    oled_nrst.high()

    display = seps525.SEPS525(160,128,spi1,oled_cs,oled_rs)
    return display

def color_oled(r,g,b):
    return (g // 32) + ((r // 8) << 3) + ((b // 8 ) << 8)
    
