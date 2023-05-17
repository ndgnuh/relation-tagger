from functools import wraps
from argparse import Namespace
from collections import defaultdict


def static(f):
    """
    Create a function with static state, the static is passed to the first parameter.
    """
    static = defaultdict(lambda *a, **k: None)

    @wraps(f)
    def wrapped(*a, **k):
        return f(static, *a, **k)

    return wrapped


def reactive_class(cls):
    """
    Create a class that allows registering reactive functions.
    """
    def __setattr__(self, k, v):
        for f in self._dispatches[k]:
            f(self, v)
        object.__setattr__(self, k, v)

    cls.__setattr__ = __setattr__
    cls._dispatches = defaultdict(list)
    return cls


def reactive(cls, key, callback=None):
    """
    Register reactive function to a class
    ```
    @reactive(Class, 'myprop')
    def callback(self, new_value):
        ...

    reactive(Class, 'myprop', callback)
    ```
    """
    def wrapper(f):
        cls._dispatches[key].append(f)
        return f

    if callback is not None:
        wrapper(callback)
    return wrapper


def requires(fields):
    """
    Wrapper for early returns, fields can be string or collection like list.
    """
    if isinstance(fields, str):
        fields = [fields]

    def wrapper(f):
        @wraps(f)
        def wrapped(state, *args, **kwargs):
            for k in fields:
                if getattr(state, k, None) is None:
                    return
            f(state, *args, **kwargs)

        return wrapped

    return wrapper
