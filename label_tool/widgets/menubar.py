from imgui_bundle import imgui, immapp
from dataclasses import dataclass
from .datastatus import datastatus

@dataclass
class MenuBarResult:
    import_btn_clicked: bool = False
    save_btn_clicked: bool = False

def draw_menu_bar(state):
    result = MenuBarResult()
    if imgui.begin_main_menu_bar():
        # File menu
        if imgui.begin_menu('File', True):
            result.import_btn_clicked, _ = imgui.menu_item('Import', 'Ctrl+O', False, True)
            clicked, _ = imgui.menu_item('Save', 'Ctrl+S', False, True)
            imgui.end_menu()

        # Datastatus
        imgui.same_line()
        imgui.separator()
        datastatus(state)
    imgui.end_main_menu_bar()

    return result
