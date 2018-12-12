from functools import partial


def callback(stream):
    def wrapper(attr, old, new):
        stream.emit(new)
    return wrapper


def click(stream):
    def wrapper():
        stream.emit()
    return wrapper


class Observable(object):
    def __init__(self, on_value):
        self.on_value = on_value

    def notify(self, value):
        self.on_value(value)


class Stream(object):
    def __init__(self):
        self.subscribers = []
        self.observables = {}

    def register(self, subscriber):
        self.subscribers.append(subscriber)

    def subscribe(self, on_value):
        observable = Observable(on_value)
        self.register(observable)
        uid = id(observable)
        self.observables[uid] = observable
        return partial(self.unsubscribe, uid)

    def unsubscribe(self, uid):
        assert isinstance(uid, int), "Unique ID should be int: {}".format(uid)
        index = self.subscribers.index(self.observables[uid])
        self.subscribers.pop(index)

    def emit(self, value=None):
        for subscriber in self.subscribers:
            subscriber.notify(value)

    def map(self, value):
        return Map(self, value)

    def flat_map(self, method):
        return FlatMap(self, method)

    def flat_map_latest(self, method):
        return FlatMapLatest(self, method)

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


class FlatMap(Stream):
    """Flat map flattens multiple streams into single stream"""
    def __init__(self, stream, method):
        if not hasattr(method, '__call__'):
            self.method = lambda x: method
        else:
            self.method = method
        stream.register(self)
        super().__init__()

    def notify(self, value):
        self.method(value).subscribe(self.emit)


class FlatMapLatest(Stream):
    """Flat map but ignores all but latest stream"""
    def __init__(self, stream, method):
        if not hasattr(method, '__call__'):
            self.method = lambda x: method
        else:
            self.method = method
        stream.register(self)
        super().__init__()
        self.unsubscribe = None

    def notify(self, value):
        if self.unsubscribe is not None:
            self.unsubscribe()
        self.unsubscribe = self.method(value).subscribe(self.emit)


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


class CombineLatest(Stream):
    def __init__(self, *streams):
        self.streams = streams
        self.state = [None for _ in streams]
        for i, stream in enumerate(streams):
            stream.subscribe(partial(self.notify, i))
        super().__init__()

    def notify(self, index, value):
        self.state[index] = value
        self.emit(tuple(self.state))


def combine_latest(*streams):
    return CombineLatest(*streams)


def scan_reset(stream, accumulator, reset):
    """Accumulate values with a stream to reset the seed"""
    return reset.flat_map_latest(lambda seed: stream.scan(seed, accumulator))


def scan_reset_emit_seed(stream, accumulator, reset, identity=0):
    """Same as scan_reset but with an identity emit on seed change

    .. note:: This method is needed to properly time order
              flat_map with scan operations
    """
    return scan(stream, reset, accumulator, identity=identity)


def scan(stream, seeds, accumulator, identity=0):
    def method(seed):
        return Merge(stream, seeds.map(identity)).scan(seed, accumulator)
    return seeds.flat_map_latest(method)
