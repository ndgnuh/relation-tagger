from dataclasses import dataclass
from typing import *
from imgui_bundle import imgui


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
                help_str=help_str or callback.__doc__
            )
            cls.shortcuts.append(shortkey)

        return wrapper

    @classmethod
    def on_frame(cls, state):
        io = imgui.get_io()
        for shortcut in cls.shortcuts:
            if io.key_mods & shortcut.mod and imgui.is_key_pressed(shortcut.key):
                shortcut.callback(state)
                return


@Shortcut.register(mod=imgui.Key.im_gui_mod_ctrl, key=imgui.Key.s)
def save(state):
    state.dataset.save()
