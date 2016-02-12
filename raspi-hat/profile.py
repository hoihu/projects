import pyb

def timed_function(f, *args, **kwargs):
    myname = str(f)
    def new_func(*args, **kwargs):
        t = pyb.micros()
        result = f(*args, **kwargs)
        delta = pyb.elapsed_micros(t)
        print('{} Time = {:6.3f}mS'.format(myname, delta/1000))
        return result
    return new_func
