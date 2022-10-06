# 1 feature -> keyboard, button, etc
import pygame
from pygame_gui.windows import (
    UIMessageWindow,
)
from spade_label_tool.ui_file_dialog import UIFileDialog
from lenses import bind
from spade_label_tool.utils import write_jsonl_ui


def init_save_file(event, state):
    data_file_to_save = state.data_file_to_save.get()
    data = state.data.get()
    ui_manager = state.ui_manager.get()
    rect = state.dialog_rect.get()
    if data is None:
        UIMessageWindow(html_message="No data to save",
                        manager=state.ui_manager.get(),
                        rect=rect)
        return state

    if data_file_to_save is not None:
        write_jsonl_ui(data_file_to_save, data)
        return state

    picker = UIFileDialog(rect=rect,
                          allow_existing_files_only=False,
                          allow_picking_directories=True,
                          window_title="Save data",
                          manager=ui_manager)
    print('allow', picker.allow_existing_files_only)
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
