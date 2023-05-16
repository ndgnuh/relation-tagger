import random
from os import path
from itertools import product
from dataclasses import dataclass
from imgui_bundle import imgui, immapp, hello_imgui
from imgui_bundle import im_file_dialog as fd
from .widgets.filepicker import pick_open_file
from .states import State
from .widgets.node_editor import NodeEditor
from .widgets import filepicker
from .widgets.dirty_indicator import dirty_indicator, save_button
from .widgets.datastatus import label_selector
from .widgets.menubar import draw_menu_bar
from .shortcuts import Shortcut

thisdir = path.dirname(__file__)


def gui(state):
    try:

        root_width, root_height = imgui.get_window_size()
        menu_height = 30

        # Menu bar
        menubar_events = draw_menu_bar(state)

        #
        # Left panel
        #
        imgui.set_next_window_pos(imgui.ImVec2(
            0, menubar_events.menubar_height))
        imgui.begin("Tools")
        imgui.set_window_size(imgui.ImVec2(root_width * 0.2, root_height))
        label_selector(state)
        imgui.end()

        #
        # Main panel
        #
        imgui.set_next_window_pos(
            imgui.ImVec2(root_width * 0.2, menubar_events.menubar_height)
        )
        imgui.begin(
            "Workspace",
            flags=imgui.WindowFlags_.no_scrollbar
        )
        imgui.set_window_size(imgui.ImVec2(root_width * 0.8, root_height))
        # if isinstance(state.error, str):
        #     imgui.set_next_window_size(
        #         imgui.ImVec2(root_width * 0.8, root_height * 0.8)
        #     )
        #     imgui.begin("Error")
        #     imgui.text(state.error)
        #     if imgui.button("OK"):
        #         state.resolve_error()
        #     imgui.end()

        # state.checkpoint()
        # imgui.dummy(imgui.ImVec2(0, 30))
        # selected_dataset = pick_open_file("Pick data", "Data file", "*jsonl")
        # if selected_dataset:
        #     state.dataset_file = selected_dataset
        # save_button(state)

        if state.node_editor is not None:
            imgui.same_line()
            state.node_editor.on_frame()
            label_selector(state)
        imgui.end()

        # handle shortcut
        Shortcut.on_frame(state)

        # Conditional widgets/popups
        # Must be drawn last
        dataset_file = filepicker.pick_open_file(
            menubar_events.import_btn_clicked)
        if dataset_file:
            state.dataset_file = dataset_file
            state.dataset
    except Exception as e:
        import traceback

        traceback.print_exc()
        state.error = str(e)


def update():
    from subprocess import run

    remote = "https://github.com/ndgnuh/spade-label-tool"
    ref = ""
    # ref = "@92ad8964504909be753a4bd771854cec1c853515"
    run(["pip", "install", f"git+{remote}{ref}"])


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--data", dest="data")
    parser.add_argument("--update", dest="update",
                        action="store_true", default=False)
    parser.add_argument("--font-size", dest="font_size", type=int, default=16)

    args = parser.parse_args()
    if args.update:
        return update()

    state = State(dataset_file=args.data)

    def run_gui():
        gui(state)

    def callback_load_font():
        io = imgui.get_io()
        io.fonts.add_font_from_file_ttf(
            path.join(thisdir, "fonts", "JuliaMono-Regular.ttf"),
            args.font_size,
            None,
            io.fonts.get_glyph_ranges_vietnamese(),
        )

    runner_params = immapp.RunnerParams()
    runner_params.callbacks.load_additional_fonts = callback_load_font
    runner_params.callbacks.show_gui = run_gui
    # runner_params.callbacks.show_menus = lambda: draw_menu_bar(state)

    # runner_params.imgui_window_params.default_imgui_window_type = imgui.Def
    # runner_params.imgui_window_params.show_menu_bar = True
    # runner_params.imgui_window_params.enable_viewports = True

    add_ons_params = immapp.AddOnsParams(
        with_node_editor=True, with_markdown=True)
    immapp.run(runner_params, add_ons_params)


if __name__ == "__main__":
    main()
