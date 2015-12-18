import time, serial
ser = serial.Serial('/dev/cu.usbmodem1452', baudrate=115200, timeout=1, interCharTimeout=1)
time.sleep(0.2)
start = last = time.time()
number_of_bytes = 0

while (1):
    if ser.inWaiting() > 0:
        data = ser.read(ser.inWaiting())
        number_of_bytes = number_of_bytes + len(data)
    now = time.time()
    if (now-last > 1):
        print("RX data length {}".format(number_of_bytes))
        mbits = (number_of_bytes * 8 / (now-start)) / 1e6
        print("Speed: {} Mbits/sec".format(mbits))
        last = now
