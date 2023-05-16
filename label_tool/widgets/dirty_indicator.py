from imgui_bundle import imgui, immapp
from ..states import requires


@requires("dataset")
def dirty_indicator(state):
    if state.dataset.dirty:
        imgui.text("*")
    else:
        imgui.text("")


@requires("dataset")
def save_button(state):
    imgui.begin_disabled(not state.dataset.dirty)
    button = imgui.button("Save")
    imgui.end_disabled()
    if button:
        state.dataset.save()
