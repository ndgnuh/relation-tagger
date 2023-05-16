from dataclasses import dataclass
from typing import *
from imgui_bundle import imgui
from .states import requires


@dataclass
class Shortcut:
    mod: Optional
    key: Any
    callback: Callable
    help_str: str = ""

    shortcuts: ClassVar[List] = []

    @classmethod
    def register(cls, mod, key, help_str=None):
        def wrapper(callback: Callable):
            shortkey = cls(
                mod=mod,
                key=key,
                callback=callback,
                help_str=help_str or callback.__doc__,
            )
            cls.shortcuts.append(shortkey)

        return wrapper

    @classmethod
    def on_frame(cls, state):
        io = imgui.get_io()
        for shortcut in cls.shortcuts:
            if ((io.key_mods & shortcut.mod) or (shortcut.mod == imgui.Key.im_gui_mod_none)) and imgui.is_key_pressed(shortcut.key):
                shortcut.callback(state)
                return


@Shortcut.register(mod=imgui.Key.im_gui_mod_ctrl, key=imgui.Key.s)
@requires("dataset")
def save(state):
    state.dataset.save()


@Shortcut.register(mod=imgui.Key.im_gui_mod_none, key=imgui.Key.d)
@requires("dataset")
def save(state):
    print("Next")
    state.dataset.next_data()


@Shortcut.register(mod=imgui.Key.im_gui_mod_none, key=imgui.Key.a)
@requires("dataset")
def save(state):
    print("Prev")
    state.dataset.previous_data()
