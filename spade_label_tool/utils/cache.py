import numpy as np
from typing import List, Dict
from plum import dispatch
from queue import Queue


@dispatch
def custom_hash(x):
    return hash(x)


@dispatch
def custom_hash(lst: List):
    __hash = 0
    for i, item in enumerate(lst):
        __hash = custom_hash((__hash, i, custom_hash(item)))
    return __hash


@dispatch
def custom_hash(d: Dict):
    __hash = 0
    keys = sorted(d.keys())
    for key in keys:
        __hash = custom_hash((__hash, key, custom_hash(d[key])))
    return __hash


@dispatch
def custom_hash(arr: np.ndarray):
    return hash(arr.tobytes())


def memoize(maxsize=None):
    def decorator(func):
        cache = {}
        cache_info = dict(size=0, keys=Queue(), maxsize=maxsize)

        def wrapper(*args, **kwargs):
            __hash = custom_hash(
                [id(func)] + list(args) + list(kwargs.items()))
            if __hash in cache:
                return cache[__hash]

            cache_size = cache_info['size']
            if maxsize is not None and cache_size >= maxsize:
                key = cache_info['keys'].get()
                cache.pop(key)
                cache_info['size'] -= 1

            cache_info['keys'].put(__hash)
            cache[__hash] = func(*args, **kwargs)
            cache_info['size'] += 1

            return cache[__hash]
        return wrapper
    return decorator
