# Example using PIO to drive a set of WS2812 LEDs.

import array, time
from machine import Pin
import rp2

# Configure the number of WS2812 LEDs.
NUM_LEDS = 9

PIO0_BASE = 0x50200000
PIO0_BASE_TXF0 = PIO0_BASE+0x10

@rp2.asm_pio(
    sideset_init=rp2.PIO.OUT_LOW,
    out_shiftdir=rp2.PIO.SHIFT_LEFT,
    autopull=True,
    pull_thresh=24,
)
def ws2812():
    # fmt: off
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()
    # fmt: on


# Create the StateMachine with the ws2812 program, outputting on Pin(2).
sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(2))

# Start the StateMachine, it will wait for data on its FIFO.
sm.active(1)

# Dummy data
ar = array.array("I", [0 for _ in range(NUM_LEDS)])
ar[0] = 0xff3f0f00
ar[1] = 0xaa00aa00

# starts the transfer, using DMA channel 0
def dma_out():
    import dma, uctypes
    dma.init_channels()
    d0=dma.CHANNELS[0]
    d0.CTRL_TRIG.EN = 0
    d0.TRANS_COUNT = NUM_LEDS
    d0.READ_ADDR = uctypes.addressof(ar)
    d0.WRITE_ADDR = PIO0_BASE_TXF0
    d0.CTRL_TRIG.INCR_WRITE = 0
    d0.CTRL_TRIG.INCR_READ = 1
    d0.CTRL_TRIG.DATA_SIZE = 2
    d0.CTRL_TRIG.EN = 1




