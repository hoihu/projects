import time,json
import serial

def drain_input(ser):
    a = ser.inWaiting()
    if a:
        drained = ser.read(a)
        print("DRAINED {}".format(drained))

write_test_script = """
import pyb
from pyb import I2C
from balancing import Balance
import json as j

from fusion import Fusion

i2c = I2C(1, I2C.MASTER)
i2c.deinit()
i2c.init(I2C.MASTER)

from sensehat import uSenseHAT
s = uSenseHAT(i2c)
fuse = Fusion()
balance = Balance(s.matrix)

Calibrate = False

# if Calibrate:
#     sw = lambda: s.read_key()
#     fuse.calibrate(s.read_magnet, sw)
#     fm = s.lsm.scale_factor_magnet
# s.lsm.write_magnet_calib([
#     int(fuse.magbias[0]*fm),
#     int(fuse.magbias[1]*fm),
#     int(fuse.magbias[2]*fm)]
# )


while (1):
    fuse.update(s.lsm.accel, s.lsm.gyro, s.lsm.magnet)
            
    # print(j.dumps(dict(heading=fuse.heading, pitch=fuse.pitch, roll=fuse.roll)))
    balance.update(fuse.heading, fuse.pitch, fuse.roll)
    # print(j.dumps(dict(accel=data_accel, gyro=data_gyro, magnet=data_magnet)))
    pyb.delay(5)

"""

def json_parser(partial_data):
    start=0
    raw_data = ''
    while True:    
        index_start = partial_data.find('{')
        index_end = partial_data.find('}')
        if not start:
            if index_start != -1 and index_end != -1:
                partial_data = yield partial_data[index_start:index_end+1]
            elif index_start != -1:
                raw_data += partial_data[index_start:]
                start = 1
                partial_data = yield None
            else:
                partial_data = yield None
        else:
            if index_end != -1:
                partial_data = yield raw_data+partial_data[:index_end+1]
                raw_data = ''
                start = 0
            else:
                raw_data += partial_data
                partial_data = yield None

def bold(msg):
    return u'\033[1m%s\033[0m' % msg
    
def color_value(color, float_value):
    return "\033[{0}m{1:3.3f}\033[0m".format(
            str(color+30),
            float_value
    )
    
def clear_line():
    print(" "*120,end='\r')
    
        
def pretty_print_raw(data):
    clear_line()
    print("Accel={0}\t{1}\t{2}\t Gyro={3}\t{4}\t{5}\t Magnet={6}\t{7}\t{8}".format(
            color_value(1,data['accel'][0]),
            color_value(1,data['accel'][1]),
            color_value(1,data['accel'][2]),
            color_value(2,data['gyro'][0]),
            color_value(2,data['gyro'][1]),
            color_value(2,data['gyro'][2]),
            color_value(3,data['magnet'][0]),
            color_value(3,data['magnet'][1]),
            color_value(3,data['magnet'][2])), end='\r'
    )
    
def pretty_print_pilot(data):
    clear_line()
    print("Heading={0}\t Pitch={1}\t Roll={2}".format(
            color_value(1,data['heading']),
            color_value(2,data['pitch']),
            color_value(3,data['roll'])), end='\r'
    )
    
def test(dev):
    ser = serial.Serial(dev, baudrate=4000000)
    ser.write(b'\x03\x03\x01\x04') # break, break, raw-repl, soft-reboot
    ser.flush()
    ser.write(bytes(write_test_script, 'ascii'))
    ser.flush()
    time.sleep(0.1)
    drain_input(ser)
    ser.write(b'\x04') # eof
    time.sleep(0.1)
    ser.flush()
    drain_input(ser)

    json_gen = json_parser('')
    json_gen.send(None)
    start = 0
    while True:
        a = ser.inWaiting()
        if a:
            response = ser.read(a)  
            print(response)
            json_data = json_gen.send(response.decode('ascii'))
            if json_data:
                data = json.loads(json_data)
                pretty_print_pilot(data)
    
port = """/dev/cu.usbmodem1432"""

def main():
    test(port)
    
if __name__ == "__main__":
    main()
