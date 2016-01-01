#!/usr/bin/env python

import time
import argparse
import threading
import serial

write_test_script = """
import sys
import pyb
pyb.LED(1).on()
b=bytearray(%u)
sys.stdout.write("Ready")

pyb.LED(1).off()
while 1:
    b = sys.stdin.read(%u)
    pyb.LED(2).toggle()
    sys.stdout.write(b)
    """
    
class VCPCommTest:
    def __init__(self, device):
        self.device = device
        self.rx_data = b''
        
    def read_until(self, pattern, timeout = 1, verbose = 0):
        self.rx_data = ''
        now = time.time()
        while((time.time() - now) < timeout):
            a = self.device.inWaiting()
            if a:
                try:
                    rx = self.device.read(1).decode('ascii')
                except UnicodeDecodeError:
                    # bad data or similar - just continue here
                    # data validation is done outside this function
                    continue
                self.rx_data = self.rx_data + rx
                if self.rx_data.find(pattern) != -1:
                    if verbose:
                        # print("RX: {}".format(rx_data))
                        print("FOUND {}".format(pattern))
                    return 1
            else:
                time.sleep(0.001)
        return 0
                
    def echo(self, data_tx, verbose = 0):
        self.device.write(bytes(data_tx))
        # self.device.write(bytes(data_tx.encode('ascii')))
        self.device.flush()
    
    def soft_reset(self):
        self.device.write(b'\x03') # break, 
        self.device.flush()
        time.sleep(0.01)
        self.device.write(b'\x03\x01\x04') # raw-repl, soft-reboot
        self.device.flush()
        return self.read_until("CTRL-B to exit\r\n>", verbose = 0)
        
            
    def write_test_script(self, script, length):
        # self.device.write(bytes(script, 'ascii'))
        self.device.write(bytes(script % (length,length), 'ascii'))
        # start script on pyboard now
        self.device.write(b'\x04')
        self.device.flush()
        return self.read_until("Ready", verbose = 0)
        

port = """/dev/cu.usbmodem1452"""
fails = []

def testrun(tester,blocksize):
    global fails
    print("Testing with blocksize {}".format(blocksize), end="")
    if not tester.soft_reset():
        print("FAILED on soft reset, no CTLR-B detected",end="")
        fails.append((0,blocksize,''))
        return
        
    if not tester.write_test_script(write_test_script,blocksize):
        print("FAILED on writing script")
        fails.append((0,blocksize,''))
        return
        
    buf = bytearray(blocksize)
    for i in range(len(buf)):
        buf[i] = 32 + (i & 0x3f) # don't want to send ctrl chars!
        
    for i in range(0,10):
        tester.echo(buf)
        if tester.read_until(buf.decode('ascii'),verbose = 0):
            # detected correct string
            print(".",end="")
        else:
            print("RX data was {} bytes instead of {}".format(len(tester.rx_data),len(buf)))
            print("====> TX: {}\n====> RX: {}".format(buf,tester.rx_data))
            fails.append((i,blocksize,tester.rx_data))
            return
    print("OK")
    
def main():
    import random
    ser = serial.Serial(port, baudrate=4000000)
    tester = VCPCommTest(ser)
    start_time = time.time()
    total_bytes = 0
    for i in range(0,100):
        # start with a random blocksize between 8-20
        # so that the testcase are slightly different
        blocksize = random.randrange(8,20)
        while (blocksize < 10000):
            blocksize *= 1.1
            total_bytes += blocksize
            testrun(tester,int(blocksize))
    end_time = time.time()
    print("Tested {}kB data in {} seconds".format(
            int(total_bytes/1000.),
            int(end_time-start_time)
    ))
    if not fails:
        print("SUCCESS")
    else:
        print("FAIL: logs: {}".format(fails))
    
if __name__ == "__main__":
    main()
