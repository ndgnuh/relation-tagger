from os import path
from imgui_bundle import imgui, immapp
from imgui_bundle import im_file_dialog

from .. import utils

fd = im_file_dialog.FileDialog.instance()


def dataset_open_picker(state):
    picker_id = "dataset_open_picker"
    title = "Open"
    description = "Dataset file (*.json)"

    # Open picker
    if state.dataset_ask_pick_file:
        fd.open(picker_id, title, description, True)

    # Check result
    if fd.is_done(picker_id):
        if fd.has_result():
            selected_file = fd.get_results()[0].path()
            state.dataset_pick_file(selected_file)
        fd.close()


@utils.requires("dataset")
def dataset_export_picker(state):
    picker_id = "dataset_export_picker"
    title = "Export as"
    description = "Dataset file (*.json)"

    if state.dataset_ask_export_file:
        fd.save(picker_id, title, description)
        state.app_shortcuts_enabled = False

    if fd.is_done(picker_id):
        if fd.has_result():
            selected_file = fd.get_results()[0].path()
            if path.exists(selected_file):
                state.dataset_ask_export_file_confirm(selected_file)
            else:
                state.dataset_export_file(selected_file)
        fd.close()
        state.app_shortcuts_enabled = True


def handle(state):
    dataset_open_picker(state)
    dataset_export_picker(state)
