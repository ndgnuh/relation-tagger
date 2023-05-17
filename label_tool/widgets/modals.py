from imgui_bundle import imgui
from ..states import State


def warn_on_exit(state: State):
    if state.dataset is None:
        return True

    if not state.dataset.dirty:
        return True

    if imgui.begin_popup("Warning"):
        imgui.text("There current dataset is not saved, what to do?");
        imgui.separator()
        imgui.button("Save and quit")
        imgui.button("Discard and quit")
        imgui.button("Cancel")
        imgui.end_popup()
    return False
