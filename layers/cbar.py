"""

Dynamic colorbar arrangements can be achieved through
a set operation on tuples ``(name, level, min, max, ...)`` that
describe a colorbar.

"""


class ColorbarLayout(object):
    """Responsible for stacking colorbar objects"""
    pass


class Collection(object):
    """Responsible for maintaining a list of colorbar glyphs"""
    pass
