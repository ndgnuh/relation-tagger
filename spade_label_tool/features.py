# 1 feature -> keyboard, button, etc
import pygame
from pygame_gui.windows import (
    UIFileDialog,
    UIMessageWindow,
)
from lenses import bind


def init_save_file(event, state):
    data = state.data.get()
    ui_manager = state.ui.manager.get()
    ww = state.ui.window_width.get()
    wh = state.ui.window_height.get()
    xpad = ww // 10
    ypad = wh // 10
    rect = pygame.Rect(xpad, ypad, ww - 2 * xpad, wh - 2 * ypad)

    if data is None:
        UIMessageWindow(html_message="No data to save",
                        manager=state.ui.manager.get(),
                        rect=rect)
        return state

    picker = UIFileDialog(rect=rect,
                          allow_picking_directories=False,
                          allow_existing_files_only=False,
                          manager=ui_manager)
    picker.id = 'picker/save'
    return state


def init_load_file(event, state):
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
