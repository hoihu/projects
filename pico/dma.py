import uctypes
from uctypes import BF_POS, BF_LEN, BFUINT32

DMA_CTRL_REG = {
        "AHB_ERROR": 31     << BF_POS | 1 << BF_LEN | BFUINT32,
        "READ_ERR": 30      << BF_POS | 1 << BF_LEN | BFUINT32,
        "WRITE_ERR": 29     << BF_POS | 1 << BF_LEN | BFUINT32,
        "Reserved": 25      << BF_POS | 4 << BF_LEN | BFUINT32,
        "BUSY": 24          << BF_POS | 1 << BF_LEN | BFUINT32,
        "SNIFF_EN": 23      << BF_POS | 1 << BF_LEN | BFUINT32,
        "BSWAP": 22         << BF_POS | 1 << BF_LEN | BFUINT32,
        "IRQ_QUIET": 21     << BF_POS | 1 << BF_LEN | BFUINT32,
        "TREQ_SEL": 15      << BF_POS | 6 << BF_LEN | BFUINT32,
        "CHAIN_TO": 11      << BF_POS | 4 << BF_LEN | BFUINT32,
        "RING_SEL": 10      << BF_POS | 1 << BF_LEN | BFUINT32,
        "RING_SIZE": 6      << BF_POS | 4 << BF_LEN | BFUINT32,
        "INCR_WRITE": 5     << BF_POS | 1 << BF_LEN | BFUINT32,
        "INCR_READ": 4      << BF_POS | 1 << BF_LEN | BFUINT32,
        "DATA_SIZE": 2      << BF_POS | 2 << BF_LEN | BFUINT32,
        "HIGH_PRIO": 1      << BF_POS | 1 << BF_LEN | BFUINT32,
        "EN": 0             << BF_POS | 1 << BF_LEN | BFUINT32,
}

DMA_LAYOUT = {
    "READ_ADDR": 0   | uctypes.UINT32,
    "WRITE_ADDR": 4  | uctypes.UINT32,
    "TRANS_COUNT": 8 | uctypes.UINT32,
    "CTRL_TRIG": (12,  DMA_CTRL_REG),
    "CTRL_TRIG_RAW": 12 | uctypes.UINT32, # for single update of all fields
    "AL1_CTRL": 16   | uctypes.UINT32,
}

# create the DMA channel structs (0-11)
CHANNELS = [uctypes.struct(0x50000000 + i * 0x40, DMA_LAYOUT) for i in range(0,12)]

# init dma channels to some default values
def init_channels():
    for i, ch in enumerate(CHANNELS):
        # no wraparound, sniff=0, swap_byte=0, irq_quiet=1
        # unpaced transfers (=0x3f). high prio=0, data_size=word, incr_r/w = true
        ch.CTRL_TRIG_RAW = 0x3f8030
        # set chain to itself, to disable chaining
        ch.CTRL_TRIG.CHAIN_TO = i

# example function to show mem->mem transfer
# dest, src can be bytearrays, size in bytes
def memcopy(ch, dest, src, size, enable=1):
    ch.CTRL_TRIG.EN = 0
    ch.WRITE_ADDR = uctypes.addressof(dest)
    ch.READ_ADDR = uctypes.addressof(src)
    ch.TRANS_COUNT = size // (1 << ch.CTRL_TRIG.DATA_SIZE)
    ch.CTRL_TRIG.EN = enable


# can be used to temporary construct the necessary DMA CTRL values
# then copy over to actual dma channel's CTRL value in one write
# e.g. 
# scratch.CHAIN_TO=2;
# scratch.DATA_SIZE=2;
# ...
# CH0.CTRL_TRIG_RAW=scratch.CTRL_TRIG_RAW
tmp = bytearray(uctypes.sizeof(DMA_LAYOUT))
scratch_ctrl = uctypes.struct(uctypes.addressof(tmp), DMA_CTRL_REG)

