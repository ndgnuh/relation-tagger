# 1 feature -> keyboard, button, etc
import pygame
from pygame_gui.windows import (
    UIFileDialog,
    UIMessageWindow,
)
from lenses import bind


def init_save_file(event, state):
    data = state.data.get()
    ui_manager = state.ui_manager.get()
    rect = state.dialog_rect.get()
    if data is None:
        UIMessageWindow(html_message="No data to save",
                        manager=state.ui_manager.get(),
                        rect=rect)
        return state

    picker = UIFileDialog(rect=rect,
                          allow_picking_directories=False,
                          allow_existing_files_only=False,
                          manager=ui_manager)
    picker.id = 'picker/save'
    return state


def init_load_file(event, state):
    ui_manager = state.ui_manager.get()
    rect = state.dialog_rect.get()
    picker = UIFileDialog(rect=rect,
                          allow_picking_directories=False,
                          allow_existing_files_only=True,
                          manager=ui_manager)
    picker.id = 'picker/load'
    return state
