import time
import bokeh.plotting

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        duration = end - start
        msg = "{} ran for {} seconds".format(str(func),
                                             duration)
        print(msg)
        return result
    return wrapper
