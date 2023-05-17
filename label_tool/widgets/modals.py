from imgui_bundle import imgui
from ..states import State


def warn_on_exit(state: State):
    if state.dataset is None:
        return False

    if not state.dataset.dirty:
        return False

    running = True
    imgui.begin("Warning")
    imgui.text("There current dataset is not saved, what to do?")
    imgui.separator()
    if imgui.button("Save and quit"):
        state.dataset.save()
        running = False
    if imgui.button("Discard and quit"):
        running = False
    imgui.end()

    return running
