from spade_label_tool.utils import Functables
from pygame_gui.windows.ui_file_dialog import (
    UIFileDialog,
    UIConfirmationDialog
)
import pygame
from lenses import bind

button_callbacks = Functables()


@button_callbacks("menu/load")
def _(event, state):
    ui_manager = state.ui.manager.get()
    ww = state.ui.window_width.get()
    wh = state.ui.window_height.get()
    xpad = ww // 10
    ypad = wh // 10
    rect = pygame.Rect(xpad, ypad, ww - 2 * xpad, wh - 2 * ypad)
    picker = UIFileDialog(rect=rect,
                          allow_picking_directories=False,
                          allow_existing_files_only=True,
                          manager=ui_manager)
    picker.id = 'picker/load'
    return state


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
    print('event', event)
    btn_id = getattr(event.dict['ui_element'], "id", None)
    print('btn_id', btn_id)
    if btn_id is None:
        print(event.dict['ui_element'], "has no button id")
        return state
    callback = button_callbacks.get(btn_id, None)
    if callback is None:
        print("callback for", btn_id, "is None")
        return state
    else:
        return callback(event, state)
