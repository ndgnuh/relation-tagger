import traceback
from imgui_bundle import imgui
from ..states import State

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


def warn_on_exit(state: State):
    if state.dataset is None:
        return False

    if not state.dataset.dirty:
        return False

    running = True
    _set_next_window_notification()
    imgui.begin("Warning", flags=flags)
    imgui.text("There current dataset is not saved, what to do?")
    imgui.separator()
    if imgui.button("Save and quit"):
        state.dataset.save()
        running = False
    if imgui.button("Discard and quit"):
        running = False
    imgui.end()

    return running


def warn_on_delete_sample(state: State):
    if not state.app_wants_delete_sample:
        return

    imgui.begin("Warning", flags=flags)
    _set_window_notification()
    imgui.text("Delete this sample? ")
    imgui.same_line()
    imgui.text_colored(red, "This action cannot be undone")

    imgui.spacing()
    imgui.push_style_color(0, red)
    if imgui.button("Yes"):
        state.app_wants_delete_sample = False
        state.dataset.delete_current_sample()
    imgui.pop_style_color()
    imgui.same_line()
    if imgui.button("No"):
        state.app_wants_delete_sample = False
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

    imgui.same_line()
    if imgui.button("Copy"):
        imgui.set_clipboard_text(state.error)
    imgui.end()

    print(state.dataset_file)
