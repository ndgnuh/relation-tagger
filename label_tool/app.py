import random
from os import path
from itertools import product
from imgui_bundle import imgui, immapp
from imgui_bundle import im_file_dialog as fd
from .widgets.filepicker import pick_open_file
from .states import State
from .widgets.node_editor import NodeEditor
from .widgets.dirty_indicator import dirty_indicator, save_button
from .shortcuts import Shortcut

thisdir = path.dirname(__file__)


def gui(state):
    try:
        root_width, root_height = imgui.get_window_size()
        if state.dataset:
            dirty_indicator(state)
            imgui.same_line()
            imgui.text(f"Selected data: {state.dataset_file}")

        if isinstance(state.error, str):
            imgui.set_next_window_size(
                imgui.ImVec2(root_width * 0.8, root_height * 0.8)
            )
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


def update():
    from subprocess import run

    remote = "https://github.com/ndgnuh/spade-label-tool"
    ref = "92ad8964504909be753a4bd771854cec1c853515"
    run(["pip", "install", f"git+{remote}@{ref}"])


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--data", dest="data")
    parser.add_argument("--update", dest="update", action="store_true", default=False)

    args = parser.parse_args()
    if args.update:
        return update()

    state = State(dataset_file=args.data)

    def run_gui():
        gui(state)

    def callback_load_font():
        io = imgui.get_io()
        io.fonts.add_font_from_file_ttf(
            path.join(thisdir, "..", "fonts", "JuliaMono-Regular.ttf"),
            20,
            None,
            io.fonts.get_glyph_ranges_vietnamese(),
        )

    runner_params = immapp.RunnerParams()
    runner_params.callbacks.load_additional_fonts = callback_load_font
    runner_params.callbacks.show_gui = run_gui

    add_ons_params = immapp.AddOnsParams(with_node_editor=True)
    immapp.run(runner_params, add_ons_params)


if __name__ == "__main__":
    main()
