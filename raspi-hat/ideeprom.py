from pyb import I2C
import struct

ATOM_INVALID_TYPE = const(0)
ATOM_VENDOR_TYPE = const(1)
ATOM_GPIO_TYPE = const(2)
ATOM_LINUX_DEV_TREE_TYPE = const(3)
ATOM_MANUF_CUSTOM_DATA_TYPE = const(4)
ATOM_HINVALID_TYPE = const(0xffff)

I2C_ADDR_EEPROM = const(0x50) 

BACK_POWER_STRS = [
    "No Backpower", 
    "Board back powers and can supply up to 1.3A to the Pi"
    "Board back powers and can supply up to 2A to the Pi"
]

class IDEEPROM:
    def __init__(self,i2c):
        self.i2c = i2c
        
    def open(self, verbose = False):
        self.read_header(verbose=verbose)
        self.atom_reader(12,verbose=verbose)
        print("HAT EEPROM:\nVendor={}, Product={}, UUID={}".format(self.vendor,self.product,self.UUID))

    def read_header(self,verbose = False):
        data = self.read_raw(0,12)
        self.signature, self.version,res, self.num_atoms, self.eeprom_data_len = struct.unpack("<4sBBHL",data)
        if verbose:
            print("{}, Ver={}, num_atoms={}, eeprom data size={} bytes".format(
                self.signature,
                self.version,
                self.num_atoms,
                self.eeprom_data_len)
            )
    
    def atom_reader(self, start_offset, store_blob = False, verbose = False):
        offset = start_offset
        for i in range(0,self.num_atoms):
            type, count, dlen = struct.unpack("<HHL", self.read_raw(offset,8))
            offset += 8
            # if verbose:
            #     print("Type={}, count={}, dlen={}".format(type,count,dlen))
            # XXX ignoring CRC here..
            data = self.read_raw(offset,dlen-2)
            offset += dlen
            if type == ATOM_VENDOR_TYPE:
                self.store_vendor(data, verbose = verbose)
            elif type == ATOM_GPIO_TYPE:
                self.store_gpio(data, verbose = verbose)
            elif type == ATOM_LINUX_DEV_TREE_TYPE:
                if store_blob:
                    self.store_device_tree(data, verbose = verbose)
            elif type == ATOM_MANUF_CUSTOM_DATA_TYPE:
                print("Custom Type - not handled")
    
    def store_device_tree(self,data,verbose = False):
        if verbose:
            print("Linux Device Tree: {}".format(data))
        self.dev_tree = data
    
    def store_gpio(self,data, verbose = False):
        bank_drive = data[0]
        self.back_power = data[1]& 0x3
        self.gpio_current = (bank_drive & 0xf) * 2
        self.gpio_slew = bank_drive >> 4 & 0x3
        self.gpio_hyst = bank_drive >> 6
        self.gpio_pins = data[2:]
        if verbose:        
            print("Drive={}mA, Slew={}, Hyst={}".format(self.gpio_current,self.gpio_slew,self.gpio_hyst))
            print("Backpower mode={}".format(BACK_POWER_STRS[self.back_power]))
            for i in range(28):
                d = data[i+2]
                print("GPIO {}: func:{}, pull:{}, is_used:{}".format(i,d & 0x7,(d>>5) & 0x3,d>>7))

    def store_vendor(self, data, verbose = False):
        # RFC 4122 compliant UUID
        ser1, ser2, ser3, ser4, self.pid, self.pver, vlen,pslen = struct.unpack("<LLLLHHBB",data)
        self.vendor, self.product = struct.unpack("<{}s{}s".format(vlen,pslen), data[22:])
        self.UUID = "{:08X}-{:04X}-{:04X}-{:04X}-{:04X}{:08X}".format(
            ser4, (ser3 & 0xffff0000) >> 16, 
            ser3 & 0xffff, (ser2 & 0xffff0000) >> 16,
            ((ser2 & 0xffff) << 16),ser1
        )
        
        if verbose:
            print("UUID={}, PID={:02X}, PVer={:02X}".format(self.UUID, self.pid, self.pver))
            print("Vendor={}, Product = {}".format(self.vendor,self.product))
        
    def read_raw(self,offset,size):
        return self.i2c.mem_read(size,I2C_ADDR_EEPROM,offset,addr_size=16)
    
eeprom = IDEEPROM(I2C(2, I2C.MASTER))
eeprom.open() 
