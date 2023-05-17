from functools import wraps
from argparse import Namespace
from collections import defaultdict

def static(f):

    static = defaultdict(lambda *a, **k: None)

    @wraps(f)
    def wrapped(*a, **k):
        return f(static, *a, **k)

    return wrapped


