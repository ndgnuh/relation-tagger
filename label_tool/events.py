from dataclasses import dataclass
from typing import TypeVar, Any, Optional, Generic
from enum import auto
from contextlib import contextmanager

T = TypeVar("T")


@dataclass
class Event(Generic[T]):
    trigger: bool = False
    value: Optional[T] = None

    def set(self, value: T = None):
        self.value = value
        self.trigger = True
        return self

    def get(self):
        return self.value

    def check(self):
        ret = (self.trigger, self.value)
        if self.trigger:
            self.trigger = False
        return ret

    # Convenience-s + compat
    def __call__(self, value=True):
        return self.set(value)

    def __bool__(self):
        return self.check()[0]


def menu_item(label, event, shortcut='', enabled=True):
    from imgui_bundle import imgui
    assert isinstance(event, Event)
    if imgui.menu_item(label, shortcut, False, enabled)[0]:
        event()


if __name__ == "__main__":
    event = Event()
    if event:
        print(1)

    event.set()
    if event:
        print(2)
