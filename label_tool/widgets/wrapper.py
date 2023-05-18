from imgui_bundle import imgui


def menu_item(label, event, shortcut="", enabled=True, value=True):
    if imgui.menu_item(label, shortcut, False, enabled)[0]:
        event(value)
        return True
    return False


def button(label, event, value=True):
    if imgui.button(label):
        event(value)
        return True
    return False
