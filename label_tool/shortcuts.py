from dataclasses import dataclass
from typing import *
from typing import get_type_hints
from copy import copy
from .states import requires, State

from imgui_bundle import imgui
Key = imgui.Key

T = TypeVar("T")


@dataclass
class Shortcut(Generic[T]):
    mod: Optional
    key: Any
    event: str
    value: T = True

    shortcuts: ClassVar[List] = []

    def __post_init__(self):
        assert self.event in get_type_hints(State), f"No such event: {self.event}"
        self.__class__.shortcuts.append(self)

    @classmethod
    def check(cls, mod, key, io=None):
        io = imgui.get_io()
        return (
            (io.key_mods & mod) or (mod == imgui.Key.im_gui_mod_none)
        ) and imgui.is_key_pressed(key)

    @classmethod
    def on_frame(cls, state):
        if not state.app_shortcuts_enabled:
            return
        io = imgui.get_io()
        for shortcut in cls.shortcuts:
            if cls.check(shortcut.mod, shortcut.key, io):
                event = getattr(state, shortcut.event)
                event(shortcut.value)
                return

for idx in range(10):
    key = getattr(imgui.Key, f"_{idx}")
    Shortcut(Key.im_gui_mod_none, key, "dataset_ask_assign_class", value=idx - 1)

Shortcut(Key.im_gui_mod_none, Key.d, "dataset_next")
Shortcut(Key.im_gui_mod_none, Key.a, "dataset_previous")
Shortcut(Key.im_gui_mod_none, Key.tab, "dataset_toggle_preview")
Shortcut(Key.im_gui_mod_ctrl, Key.o, "dataset_ask_pick_file")
Shortcut(Key.im_gui_mod_ctrl, Key.s, "dataset_save_file")
Shortcut(Key.im_gui_mod_ctrl, Key.e, "dataset_ask_export_file")
Shortcut(Key.im_gui_mod_ctrl, Key.i, "app_function_not_implemented")

Shortcut(Key.im_gui_mod_none, Key.s, "node_editor_add_links")
Shortcut(Key.im_gui_mod_none, Key.r, "node_editor_remove_links")
Shortcut(Key.im_gui_mod_ctrl, Key.c, "node_editor_copy_text")

Shortcut(Key.im_gui_mod_none, Key.c, "command_palette_show")
