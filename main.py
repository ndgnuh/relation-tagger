from imgui_bundle import imgui, immapp
from imgui_bundle import im_file_dialog as fd
from demo import demo_imfile_dialog
from label_tool.widgets.filepicker import pick_open_file
from label_tool.states import State


def main(state):
    if state.dataset:
        imgui.text(f"Selected data: {state.dataset_file}")

    if state.error is not None:
        imgui.set_next_window_size(imgui.ImVec2(500, 120))
        imgui.begin("Error")
        imgui.text(state.error)
        if imgui.button("OK"):
            state.resolve_error()
        imgui.end()

    selected_dataset = pick_open_file("Pick data", "Data file", "*jsonl")
    if selected_dataset:
        state.dataset_file = selected_dataset
        print(selected_dataset)


state = State(0)
immapp.run(gui_function=lambda: main(state))
