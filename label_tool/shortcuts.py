from dataclasses import dataclass
from typing import *
from imgui_bundle import imgui
from copy import copy
from .states import requires, State


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
    def check(cls, mod, key, io=None):
        io = imgui.get_io()
        return (
            (io.key_mods & mod) or (mod == imgui.Key.im_gui_mod_none)
        ) and imgui.is_key_pressed(key)

    @classmethod
    def on_frame(cls, state):
        io = imgui.get_io()
        for shortcut in cls.shortcuts:
            if cls.check(shortcut.mod, shortcut.key, io):
                shortcut.callback(state)
                return


@Shortcut.register(mod=imgui.Key.im_gui_mod_ctrl, key=imgui.Key.s)
@requires("dataset")
def save(state):
    state.dataset.save()


@Shortcut.register(mod=imgui.Key.im_gui_mod_none, key=imgui.Key.d)
@requires("dataset")
def save(state):
    state.dataset.next_data()


@Shortcut.register(mod=imgui.Key.im_gui_mod_none, key=imgui.Key.a)
@requires("dataset")
def save(state):
    state.dataset.previous_data()


@Shortcut.register(mod=imgui.Key.im_gui_mod_none, key=imgui.Key.tab)
def toggle_im_preview(state):
    state.toggle_show_image_preview()


# Because python fucking leaks the loop index
class SetNodeClass:
    def __init__(self, idx):
        self.idx = idx

    def __call__(self, state):
        if state.dataset is None:
            return
        data = state.dataset

        for node in state.node_editor_selections:
            data.set_text_class(node.id, self.idx - 1)


for idx in range(10):
    key = getattr(imgui.Key, f"_{idx}")
    Shortcut.register(mod=imgui.Key.im_gui_mod_none, key=key)(SetNodeClass(idx))
    del idx


@Shortcut.register(mod=imgui.Key.im_gui_mod_ctrl, key=imgui.Key.o)
def class_selector(state):
    state.show_data_picker = True

@Shortcut.register(mod=imgui.Key.im_gui_mod_none, key=imgui.Key.s)
def ned_add_links(state):
    state.node_editor_add_links = True

@Shortcut.register(mod=imgui.Key.im_gui_mod_none, key=imgui.Key.r)
def ned_del_links(state: State):
    state.node_editor_remove_links = True

@Shortcut.register(mod=imgui.Key.im_gui_mod_none, key=imgui.Key.c)
def cmd_plt_show(state: State):
    state.command_palette_show = True
