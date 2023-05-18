from imgui_bundle import imgui, immapp
from dataclasses import dataclass
from .data_widgets import datastatus
from .wrapper import menu_item

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
            menu_item('Open', state.dataset_ask_pick_file, 'Ctrl+O')
            menu_item('Save', state.dataset_save_file, 'Ctrl+S')
            menu_item('Export', state.dataset_ask_export_file, 'Ctrl+E')
            menu_item('Import', state.app_function_not_implemented, 'Ctrl+I')
            imgui.end_menu()

        # Datastatus
        imgui.same_line()
        imgui.separator()
        datastatus(state)
    imgui.end_main_menu_bar()

    return result
