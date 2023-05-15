from imgui_bundle import imgui, immapp
from imgui_bundle import im_file_dialog

fd = im_file_dialog.FileDialog.instance()

@immapp.static()
def pick_open_file(button, title, description):
    selected_file = None
    picker_id = f"{button}-picker"

    if imgui.button(button):
        fd.open(picker_id, title, description, True)

    if fd.is_done(picker_id):
        if fd.has_result():
            selected_file = fd.get_results()[0].path()
        fd.close()

    return selected_file
