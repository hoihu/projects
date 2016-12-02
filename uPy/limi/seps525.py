import pyb
import struct
import framebuf

# origin from https://github.com/tobbad/micropython_lib
# modified to work with framebuffer

class COM():

    debug = False

    def __init__(self, spi, cs, rs):
        self.__spi = spi
        self.__cs = cs
        self.__rs = rs

    def __data_start(self):
        self.__cs.value(0)
        self.__rs.value(0)
        self.__spi.send(0x22)
        self.__rs.value(1)
        # Switch to 16 bit transfer ?

    def __data_end(self):
        # Switch back to 8 bit transfer ?
        self.__cs.value(1)

    def write_reg(self, addr, value):
        self.__cs.value(0)
        self.__rs.value(0)
        self.__spi.send(addr)
        self.__rs.value(1)
        self.__cs.value(1)
        self.__cs.value(0)
        self.__spi.send(value)
        self.__cs.value(1)

    def send_cmd(self, cmd):
        self.__rs.value(0)
        self.__cs.value(0)
        self.__spi.send(cmd)
        self.__cs.value(1)
        self.__rs.value(1)

    def send_data(self, data):
        self.__data_start()
        self.__spi.send(data)
        self.__data_end()


class SEPS525():

    # Copy modify paste from LBF_OLED_Init default configuration which is
    # taken from DD-160128FC-1A.pdf
    
    CONF = ((0x06, 0x00), (0x02, 0x01), (0x80, 0x00),
            (0x03, 0x30),
            # Driving current R G B - default R = 82uA / G = 56uA / B = 58uA
            (0x10, 0x52), (0x11, 0x38), (0x12, 0x3A),
            # Precharge time RGB
            (0x08, 0x01), (0x09, 0x01), (0x0A, 0x01),
            # Precharge current R G B
            (0x0B, 0x0A), (0x0C, 0x0A), (0x0D, 0x0A),
            #    * Display mode set :
            #     *  - RGB
            #     *  - Column = 0->159
            #     *  - Column data display = Normal display
            #     *
            (0x13, 0x00),
            # External interface mode=MPU
            (0x14, 0x11),     # 0x01 ?
            #   * Memory write mode :
            #     *  - 8 bits dual transfer
            #     *  - 65K support
            #     *  - Horizontal address counter is increased
            #     *  - Vertical address counter is increased
            #     *  - The data is continuously written horizontally
            #     *
            (0x16, 0x66),
            # Duty = 128
            (0x28, 0x7F),
            # Display start on line 0
            (0x29, 0x00),
            # DDRAM read address start point 0x2E~0x2F
            (0x2E, 0x00),     # X
            (0x2F, 0x00),     # Y
            # Display screen saver size 0x33~0x36
            (0x33, 0x00),     # Screen saver columns start
            (0x34, 0x9F),     # Screen saver columns end
            (0x35, 0x00),     # Screen saver row start
            (0x36, 0x7F))     # Screen saver row end

    def __init__(self, width, height, spi, cs, rs):
        self.width = width
        self.height = height
        self.buffer = bytearray(self.width * self.height * 2)
        self.framebuf = framebuf.FrameBuffer(self.buffer, self.width, self.height,1)
        
        self.__com = COM(spi, cs, rs)
        
        self.__com.write_reg(0x04, 0x01)
        pyb.delay(10)
        self.__com.write_reg(0x04, 0x00)
        pyb.delay(10)
        for adr, val in self.CONF:
            self.__com.write_reg(adr, val)
        self.__color = 0x0000
        self._poweron()
        self.framebuf.fill(0)

    def _poweron(self):
        self.__com.write_reg(0x06, 0x01)
        
    def show(self):
        self.__com.write_reg(0x17, 0)   # X start
        self.__com.write_reg(0x18, self.width-1)   # X end
        self.__com.write_reg(0x19, 0)   # Y start
        self.__com.write_reg(0x1A, self.height-1)   # Y end
        self.__com.write_reg(0x20, 0)   # memory accesspointer x
        self.__com.write_reg(0x21, 0)   # memory accesspointer y
        self.__com.send_data(self.buffer)
        
