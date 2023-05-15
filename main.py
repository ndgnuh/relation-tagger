from dataclasses import dataclass
from typing import *
from imgui_bundle import imgui, immapp
from imgui_bundle import im_file_dialog as fd
from demo import demo_imfile_dialog
from label_tool.widgets.filepicker import pick_open_file


@dataclass
class State:
    count: int = 0
    selected_file: Optional[str] = None


@immapp.static(flag=False)
def toggle():
    static = toggle
    imgui.text(f"Flag: {static.flag}")
    if imgui.button("toggle"):
        static.flag = not static.flag

    return static.flag


def pick_file(button, picker_id):
    from imgui_bundle import im_file_dialog as ifd

    if imgui.button(button):
        ifd.FileDialog.instance().open(
            picker_id,
            "Open dataset",
            "Dataset file (*.jsonl)",
            True,
        )
    selected_filename = None
    if ifd.FileDialog.instance().is_done(picker_id):
        if ifd.FileDialog.instance().has_result():
            # get_results: plural form - ShaderOpenDialog supports multi-selection
            res = ifd.FileDialog.instance().get_results()
            filenames = [f.path() for f in res]
            selected_filename = "\n  ".join(filenames)

        ifd.FileDialog.instance().close()

    return selected_filename

def main(state):
    if state.selected_file:
        imgui.text(f"Selected data: {state.selected_file}")
    # imgui.text(f"Count: {state.count}")
    # imgui.same_line()
    # plus = imgui.button("+")
    # imgui.same_line()
    # minus = imgui.button("-")
    # if plus:
    #     state.count += 1
    # if minus:
    #     state.count -= 1
    # imgui.same_line()
    # toggler = toggle()

    selected_file = pick_open_file("Pick data", "Data file", "*jsonl")
    # selected_file = pick_file("Pick data", "AB")
    if selected_file:
        state.selected_file = selected_file
        print(selected_file)



state = State(0)
immapp.run(gui_function=lambda: main(state))
