from spade_label_tool.utils import Functables
from pygame_gui.windows import (
    UIFileDialog,
    UIMessageWindow,
)
import pygame
from lenses import bind
from spade_label_tool import features

button_callbacks = Functables()


button_callbacks("menu/save", features.init_save_file)
button_callbacks("menu/load", features.init_load_file)


@button_callbacks("dynamic/textbox")
def textbox_select(event, state):
    button = event.dict['ui_element']
    idx = button.index
    selection = list(state.selection.get())
    if idx in selection:
        selection = [jdx for jdx in selection if idx != jdx]
    else:
        selection = selection + [idx]
    state = bind(state.selection.set(tuple(selection)))
    return state


def event_handler(event, state):
    print('event', event.ui_element)
    btn_id = getattr(event.dict['ui_element'], "id", None)
    if btn_id is None:
        print(event.dict['ui_element'], "has no button id")
        return state
    callback = button_callbacks.get(btn_id, None)
    if callback is None:
        print("callback for", btn_id, "is None")
        return state
    else:
        return callback(event, state)
