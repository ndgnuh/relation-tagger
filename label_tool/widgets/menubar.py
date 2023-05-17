from imgui_bundle import imgui, immapp
from dataclasses import dataclass
from .data_widgets import datastatus

@dataclass
class MenuBarResult:
    menubar_width: int = 0
    menubar_height: int = 0
    import_btn_clicked: bool = False
    save_btn_clicked: bool = False

def draw_menu_bar(state):
    result = MenuBarResult()
    if imgui.begin_main_menu_bar():
        state.app_menubar_height = imgui.get_window_height()

        # File menu
        if imgui.begin_menu('File', True):
            if imgui.menu_item('Import', 'Ctrl+O', False, True)[0]:
                state.show_data_picker = True
            if imgui.menu_item('Save', 'Ctrl+S', False, True)[0]:
                state.app_wants_save_data = True
            imgui.end_menu()

        # Datastatus
        imgui.same_line()
        imgui.separator()
        datastatus(state)
    imgui.end_main_menu_bar()

    return result
