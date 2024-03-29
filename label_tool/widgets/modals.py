import traceback
from imgui_bundle import imgui
from ..states import State, loop_on
from .. import utils
from .wrapper import button

flags = imgui.WindowFlags_.no_move and imgui.WindowFlags_.no_collapse
red = imgui.ImVec4(1, 0.5, 0.5, 1)


def _set_next_window_notification():
    rw, rh = imgui.get_main_viewport().size
    x = rw / 5
    y = rh / 5
    w = rw - x - x
    h = rh - y - y
    imgui.set_next_window_size(imgui.ImVec2(w, h))
    imgui.set_next_window_pos(imgui.ImVec2(x, y))
    imgui.set_next_window_focus()


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


def dataset_ask_export_file_confirm(state: State):
    event = state.dataset_ask_export_file_confirm
    if not event:
        return

    action = False

    _set_next_window_notification()
    imgui.begin("Export file", flags=flags)
    imgui.text_colored(red, "File exists, overwrite?")
    action = action or button("Ok", state.dataset_export_file, value=event.value)
    action = action or imgui.button("Cancel")
    imgui.end()

    if not action:
        event()


@utils.static
def info_app_processing(static, state: State):
    if state.app_is_processing is None:
        static['count'] = 0
        return

    static['count'] = static.get('count', 0) + 1
    static['count'] = static['count'] % 1000
    static['dot_count'] = static.get('dot_count', 0)

    if static['count'] % 6 == 0:
        static['dot_count'] = static.get('dot_count', 0) + 1
        static['dot_count'] = static.get('dot_count', 0) % 5

    _set_next_window_notification()
    imgui.begin("Please wait", flags=flags)
    imgui.text(state.app_is_processing + "." * (static['dot_count'] + 1))
    imgui.end()


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


def warn_function_not_implemented(state):
    if not state.app_function_not_implemented:
        return

    _set_next_window_notification()
    imgui.begin("Sorry", flags=flags)
    imgui.text("This function is not implemented, open an issue at my GitHub")
    action = imgui.button("OK")
    imgui.end()

    not action and state.app_function_not_implemented()


def handle(state: State):
    show_errors(state)
    warn_on_exit(state)
    warn_on_delete_sample(state)
    dataset_ask_export_file_confirm(state)
    info_app_processing(state)
    warn_function_not_implemented(state)
