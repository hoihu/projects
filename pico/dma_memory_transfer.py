import dma

dma.init_channels()

a = bytearray(100)
b = bytearray(100)

print("Before: b={}".format(b))
# copy some stuff to a
for i in range(0,100):
    a[i] = i

# copy a -> b using dma channel 0
dma.memcopy(dma.CHANNELS[0], b, a, 100)

print("After: b={}".format(b))
