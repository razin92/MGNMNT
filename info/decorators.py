import time

def timer(f):
    def tmp(*args, **kwargs):
        t = time.time()
        res = f(*args, **kwargs)
        print("Время выполнения: %f" % (time.time()-t))
        return res
    return tmp

def pause(f):
    def tmp(*args, **kwargs):
        time.sleep(5)
        return f(*args, **kwargs)
    return tmp
