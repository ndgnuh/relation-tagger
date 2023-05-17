from imgui_bundle import imgui, immapp
from imgui_bundle import im_file_dialog

fd = im_file_dialog.FileDialog.instance()

def pick_open_file(state, title="Open a file", description="Open a file"):
    selected_file = None
    picker_id = f"file-picker"

    if state.show_data_picker:
        fd.open(picker_id, title, description, True)
        state.show_data_picker = False

    if fd.is_done(picker_id):
        if fd.has_result():
            selected_file = fd.get_results()[0].path()
        fd.close()

    return selected_file
