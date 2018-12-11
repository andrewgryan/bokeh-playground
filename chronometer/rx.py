

def callback(stream):
    def wrapper(attr, old, new):
        stream.emit(new)
    return wrapper


class Observable(object):
    def __init__(self, on_value):
        self.on_value = on_value

    def notify(self, value):
        self.on_value(value)


class Stream(object):
    def __init__(self):
        self.subscribers = []

    def register(self, subscriber):
        self.subscribers.append(subscriber)

    def subscribe(self, on_value):
        self.register(Observable(on_value))

    def emit(self, value=None):
        for subscriber in self.subscribers:
            subscriber.notify(value)

    def map(self, value):
        return Map(self, value)

    def merge(self, stream):
        return Merge(self, stream)

    def scan(self, initial, combinator):
        return Scan(self, initial, combinator)

    def filter(self, criteria):
        return Filter(self, criteria)

    def log(self):
        return Log(self)


class Map(Stream):
    def __init__(self, stream, method):
        if not hasattr(method, '__call__'):
            self.method = lambda x: method
        else:
            self.method = method
        stream.register(self)
        super().__init__()

    def notify(self, value):
        self.emit(self.method(value))


class Merge(Stream):
    def __init__(self, *streams):
        self.streams = streams
        for i, stream in enumerate(streams):
            stream.subscribe(self.notify)
        super().__init__()

    def notify(self, value):
        self.emit(value)


class Scan(Stream):
    def __init__(self, stream, initial, combinator):
        self.state = initial
        self.combinator = combinator
        stream.register(self)
        super().__init__()

    def notify(self, value):
        self.state = self.combinator(self.state, value)
        self.emit(self.state)


class Filter(Stream):
    def __init__(self, stream, criteria):
        self.criteria = criteria
        stream.register(self)
        super().__init__()

    def notify(self, value):
        if self.criteria(value):
            self.emit(value)


class Log(Stream):
    def __init__(self, stream):
        stream.register(self)
        super().__init__()

    def notify(self, value):
        print(value)
        self.emit(value)
