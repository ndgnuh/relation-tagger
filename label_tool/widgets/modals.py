import traceback
from imgui_bundle import imgui
from ..states import State, loop_on

flags = imgui.WindowFlags_.no_move and imgui.WindowFlags_.no_collapse
red = imgui.ImVec4(1, 0.5, 0.5, 1)


def _set_next_window_notification():
    w, h = imgui.get_main_viewport().size
    pos_size = imgui.ImVec2(w / 3, h / 3)
    imgui.set_next_window_size(pos_size)
    imgui.set_next_window_pos(pos_size)
    imgui.set_next_window_focus()


def _set_window_notification():
    w, h = imgui.get_main_viewport().size
    pos_size = imgui.ImVec2(w / 3, h / 3)
    imgui.set_window_size(pos_size)
    imgui.set_window_pos(pos_size)
    imgui.set_window_focus()


@loop_on("app_ask_exit")
def warn_on_exit(state: State):
    if state.dataset is None or not state.dataset.dirty:
        state.app_is_runnning = False
        return

    _set_next_window_notification()
    imgui.begin("Warning", flags=flags)
    imgui.text("There current dataset is not saved, what to do?")
    imgui.separator()
    if imgui.button("Save and quit"):
        state.dataset_save_file()
        state.app_is_runnning = False
    if imgui.button("Discard and quit"):
        state.app_is_runnning = False

    imgui.end()
    return state.app_is_runnning



@loop_on("dataset_ask_delete_sample")
def warn_on_delete_sample(state: State):
    _set_next_window_notification()

    imgui.begin("Warning", flags=flags)
    # Warn text
    imgui.text("Delete this sample? ")
    imgui.same_line()
    imgui.text_colored(red, "This action cannot be undone")

    # if button clicked
    cont = True

    # Yes delete
    imgui.spacing()
    imgui.push_style_color(0, red)
    if imgui.button("Yes"):
        state.dataset_delete_sample()
        cont = False
    imgui.pop_style_color()

    # No dont delete
    imgui.same_line()
    if imgui.button("No"):
        cont = False
    imgui.end()

    # If continue event
    return cont


def show_errors(state: State):
    if state.error is None:
        return

    trace = traceback.format_exc()
    _set_next_window_notification()
    imgui.begin("Error", flags=flags)
    imgui.text("Something has gone wrong, here are the details:")
    imgui.text_colored(red, state.error)
    if imgui.button("OK"):
        state.resolve_error()
        cont = False

    imgui.same_line()
    if imgui.button("Copy"):
        imgui.set_clipboard_text(state.error)
    imgui.end()


def handle(state: State):
    show_errors(state)
    warn_on_exit(state)
    warn_on_delete_sample(state)
