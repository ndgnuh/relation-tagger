from spade_label_tool.utils import Functables, read_jsonl, write_jsonl_ui
from spade_label_tool.data import converge_data
from pygame_gui.windows import UIConfirmationDialog, UIMessageWindow
from pygame import Rect
from lenses import bind
from os import path

picker_callbacks = Functables()


@picker_callbacks("picker/load")
def load(event, state):
    data, error = read_jsonl(event.text)
    if data is None:
        rect = Rect(0, 0, 1000, 1000)
        UIMessageWindow(html_message=f"Error {error}",
                        manager=state.ui_manager.get(),
                        rect=rect)

    else:
        # Converge data
        # TODO: safe call
        data = converge_data(data)

        # Set new data
        state = bind(state.data.set(data))
        state = bind(state.data_index.set(0))

    return state


@picker_callbacks("picker/save")
def save(event, state):
    filepath = event.text
    data = state.data.get()
    rect = Rect(0, 0, 1000, 1000)
    if path.isfile(filepath):
        confirm_save_file = UIConfirmationDialog(manager=state.ui_manager.get(),
                                                 action_long_desc=f"Overwrite {filepath}",
                                                 rect=rect)
        confirm_save_file.action = "save_data"
        confirm_save_file.data = data
        confirm_save_file.filepath = filepath

    else:
        write_jsonl_ui(state, path, data)

    return state


def handle_pickers(event, state):
    btn_id = getattr(event.dict['ui_element'], "id", None)
    if btn_id is None:
        print(event.dict['ui_element'], "has no id")
        return state
    callback = picker_callbacks.get(btn_id, None)
    if callback is None:
        print("callback for", btn_id, "is None")
        return state
    else:
        return callback(event, state)
