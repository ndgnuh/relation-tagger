from dataclasses import dataclass
from imgui_bundle import imgui, immapp
from imgui_bundle import im_file_dialog as fd
from demo import demo_imfile_dialog


@dataclass
class State:
    count: int = 0


@immapp.static(flag=False)
def toggle():
    static = toggle
    imgui.text(f"Flag: {static.flag}")
    if imgui.button("toggle"):
        static.flag = not static.flag

    return static.flag


@immapp.static()
def pick_file(picker_id):
    from imgui_bundle import im_file_dialog as ifd

    ifd.FileDialog.instance().open(
        picker_id,
        "Open dataset",
        "Dataset file (*.jsonl)",
        True,
    )
    print(2)
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
    imgui.text(f"Count: {state.count}")
    imgui.same_line()
    plus = imgui.button("+")
    imgui.same_line()
    minus = imgui.button("-")
    if plus:
        state.count += 1
    if minus:
        state.count -= 1
    imgui.same_line()
    toggler = toggle()

    if imgui.button("pick a file"):
        print(1)
        selected_file = pick_file("Pick data")



state = State(0)
immapp.run(gui_function=lambda: main(state))
