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

@timer
def main():
    """Minimal bokeh web page"""
    figure = bokeh.plotting.figure()
    figure.circle([1, 2, 3], [1, 2, 3], fill_color="lightblue")
    document = bokeh.plotting.curdoc()
    document.add_root(figure)


if __name__ == '__main__' or __name__.startswith("bk"):
    main()
