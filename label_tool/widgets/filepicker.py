from imgui_bundle import imgui, immapp
from imgui_bundle import im_file_dialog

fd = im_file_dialog.FileDialog.instance()

def dataset_open_picker(state):
    picker_id = 'dataset_open_picker'
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


def handle(state):
    dataset_open_picker(state)
