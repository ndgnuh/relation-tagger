from imgui_bundle import imgui


def menu_item(label, event, shortcut="", enabled=True, value=True):
    if imgui.menu_item(label, shortcut, False, enabled)[0]:
        event(value)
