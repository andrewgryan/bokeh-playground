

def apply_middleware(store, dispatch, middlewares):
    def wrapper(action):
        for middleware in reversed(middlewares):
            pass
        return dispatch(action)
    return wrapper


class Observable(object):
    def __init__(self):
        self.subscribers = []

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)

    def notify(self, value):
        for subscriber in self.subscribers:
            subscriber(value)


class Store(Observable):
    def __init__(self, middlewares=None):
        self.state = None
        self.reducer = reducer
        if middlewares is not None:
            mws = [m(self) for m in middlewares]
            f = self.dispatch
            for mw in reversed(mws):
                f = mw(f)
            self.dispatch = f
        super().__init__()

    def dispatch(self, action):
        self.state = self.reducer(self.state, action)
        self.notify(self.state)


def dedupe(store):
    def inner(next_method):
        previous = None
        def inner_most(action):
            nonlocal previous
            if action != previous:
                next_method(action)
            previous = action
        return inner_most
    return inner


def echo(store):
    def inner(next_method):
        def inner_most(action):
            next_method(action)
            next_method(action)
        return inner_most
    return inner


class Log(object):
    def __init__(self):
        self.actions = []

    def __call__(self, store):
        def inner(next_method):
            def inner_most(action):
                self.actions.append(action)
                return next_method(action)
            return inner_most
        return inner


def reducer(state, action):
    return {"value": action}
