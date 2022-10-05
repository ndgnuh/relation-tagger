from plum import dispatch
from typing import Callable


class Functables(dict):
    @dispatch
    def register(self, key: str):
        def register_(f: Callable):
            self[key] = f

        return register_

    @dispatch
    def register(self, key: str, f: Callable):
        self[key] = f
        return self

    def __call__(self, *args, **kw):
        return self.register(*args, **kw)
