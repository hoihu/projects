from pyb import I2C

import lsm9ds1 as lsm9

ls = lsm9.LSM9DS1(I2C(1,I2C.MASTER))

ls.init_gyro_accel()
