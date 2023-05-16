import random
from itertools import product
from imgui_bundle import imgui, immapp
from imgui_bundle import im_file_dialog as fd
from .widgets.filepicker import pick_open_file
from .states import State
from .widgets.node_editor import NodeEditor
from .widgets.dirty_indicator import dirty_indicator, save_button
from .shortcuts import Shortcut


def gui(state):
    try:
        root_width, root_height = imgui.get_window_size()
        if state.dataset:
            dirty_indicator(state)
            imgui.same_line()
            imgui.text(f"Selected data: {state.dataset_file}")

        if isinstance(state.error, str):
            imgui.set_next_window_size(imgui.ImVec2(root_width * 0.8, root_height * 0.8))
            imgui.begin("Error")
            imgui.text(state.error)
            if imgui.button("OK"):
                state.resolve_error()
            imgui.end()

        state.checkpoint()
        imgui.begin_group()
        selected_dataset = pick_open_file("Pick data", "Data file", "*jsonl")
        if selected_dataset:
            state.dataset_file = selected_dataset
        save_button(state)
        imgui.end_group()

        if state.node_editor is not None:
            imgui.same_line()
            imgui.begin_group()
            state.node_editor.on_frame()
            imgui.end_group()

        Shortcut.on_frame(state)
    except Exception as e:
        import traceback
        traceback.print_exc()
        state.error = str(e)

def main():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("--data", dest="data")

    args = parser.parse_args()

    state = State(dataset_file=args.data)

    def run_gui():
        gui(state)
    immapp.run(gui_function=run_gui, with_node_editor=True)


if __name__ == "__main__":
    main()
