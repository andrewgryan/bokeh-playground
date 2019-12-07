"""
Monadic implementation of redux middleware

Python's generator is a natural Monad structure with a
fairly simple implementation of bind and pure
"""


def null(action):
    return []


def pass_through(action):
    yield action


def double(action):
    yield action
    yield action


def add_one(action):
    yield action + 1


def pure(action):
    """Wrap action in generator"""
    yield action


def bind(generator, middleware):
    for action in generator:
        for _action in middleware(action):
            yield _action


def dispatch(middlewares, action):
    monad = pure(action)
    for middleware in middlewares:
        monad = bind(monad, middleware)
    return monad
