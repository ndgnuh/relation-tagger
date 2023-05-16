import random
from itertools import product
from imgui_bundle import imgui, immapp
from imgui_bundle import im_file_dialog as fd
from demo import demo_imfile_dialog
from label_tool.widgets.filepicker import pick_open_file
from label_tool.states import State
from label_tool.widgets.node_editor import NodeEditor


def main(state):
    root_width, root_height = imgui.get_window_size()
    if state.dataset:
        imgui.text(f"Selected data: {state.dataset_file}")

    if isinstance(state.error, str):
        imgui.set_next_window_size(imgui.ImVec2(root_width * 0.8, root_height * 0.8))
        imgui.begin("Error")
        imgui.text(state.error)
        if imgui.button("OK"):
            state.resolve_error()
        imgui.end()

    selected_dataset = pick_open_file("Pick data", "Data file", "*jsonl")
    if selected_dataset:
        state.dataset_file = selected_dataset
        print(selected_dataset)

    if state.node_editor is not None:
        imgui.same_line()
        imgui.begin_group()
        state.node_editor.on_frame()
        imgui.end_group()


state = State(0)
immapp.run(gui_function=lambda: main(state),
           with_node_editor=True)
