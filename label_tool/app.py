import random
from os import path
from itertools import product
from dataclasses import dataclass
from imgui_bundle import imgui, immapp, hello_imgui
from imgui_bundle import im_file_dialog as fd
from .states import State
from .widgets.node_editor import NodeEditor, node_editor
from .widgets import filepicker
from .widgets.dirty_indicator import dirty_indicator, save_button
from .widgets.data_widgets import label_selector
from .widgets import (
    data_widgets as dw,
    modals,
    filepicker
)
from .widgets.wrapper import menu_item
from .widgets.menubar import draw_menu_bar
from .shortcuts import Shortcut
from label_tool.widgets.cmd import command_palette

thisdir = path.dirname(__file__)


def gui(state):
    try:
        root_width, root_height = imgui.get_window_size()
        menu_height = 30

        # Menu bar
        draw_menu_bar(state)

        #
        # Left panel
        #
        imgui.begin_group()

        # First window, with toolbox and stuffs
        imgui.set_next_window_pos(imgui.ImVec2(0, state.app_menubar_height))
        imgui.begin(
            name="Tools",
            flags = imgui.WindowFlags_.no_collapse
        )

        dw.sample_navigator(state)
        imgui.spacing()
        dw.node_navigator(state)
        imgui.spacing()

        imgui.separator()
        imgui.text_disabled("Misc")
        imgui.separator()
        imgui.bullet()
        imgui.begin_group()
        menu_item("Show shortcuts", state.app_function_not_implemented, "Ctrl+/")
        imgui.text_wrapped("(This functionality is not implemented)")
        imgui.end_group()
        imgui.bullet()
        menu_item("Toggle thumbnail", state.dataset_toggle_preview, "Tab")

        # Node editor node positions
        imgui.bullet()
        menu_item("Reset node editor positions", state.node_editor_reinit, "")

        # Number of node editor initials
        imgui.bullet()
        imgui.begin_group()
        imgui.text("Number of class initials to display")
        _, value = imgui.input_int(
            "##node-editor-num-class-initials",
            state.node_editor_num_class_initials,
        )
        state.node_editor_num_class_initials = max(value, 0)
        imgui.end_group()

        imgui.bullet()
        menu_item("Debug", state.app_function_not_implemented, "")
        command_palette(state)


        # End left panel
        left_panel_with = imgui.get_window_width()
        left_panel_height = imgui.get_window_height()
        imgui.end()

        # Image preview window
        imgui.set_next_window_pos(imgui.ImVec2(0, left_panel_height + 20))
        imgui.set_next_window_size(imgui.ImVec2(left_panel_with, root_height - left_panel_height - 20))
        imgui.begin(name="Preview image",
                    flags=imgui.WindowFlags_.no_title_bar and imgui.WindowFlags_.no_move and imgui.WindowFlags_.no_decoration)
        dw.image_preview(state)
        imgui.end()
        imgui.end_group()

        #
        # Main panel
        # This one only have a node editor
        #
        imgui.set_next_window_pos(
            imgui.ImVec2(left_panel_with, state.app_menubar_height)
        )
        imgui.set_next_window_size(imgui.ImVec2(root_width - left_panel_with, root_height))
        imgui.same_line()
        imgui.begin(
            name="Workspace",
            flags=imgui.WindowFlags_.no_scrollbar and imgui.WindowFlags_.no_collapse
        )
        node_editor(state)
        imgui.end()


        # handle shortcut
        Shortcut.on_frame(state)

        # Conditional widgets/popups
        # Modal to warn on exit
        # it still quits after the dataset is saved


        filepicker.handle(state)
        modals.handle(state)
        state.handle()
    except Exception as e:
        import traceback
        trace = traceback.format_exc()
        traceback.print_exc()
        state.error = str(e) + "\n" + trace


def update():
    from subprocess import run

    remote = "https://github.com/ndgnuh/relation-tagger"
    ref = ""
    # ref = "@92ad8964504909be753a4bd771854cec1c853515"
    run(["pip", "install", f"git+{remote}{ref}"])


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("--data", dest="data")
    parser.add_argument("--update", dest="update", action="store_true", default=False)
    parser.add_argument("--font-size", dest="font_size", type=int, default=16)

    args = parser.parse_args()
    if args.update:
        return update()

    state = State()
    state.dataset_pick_file(args.data)
    runner_params = immapp.RunnerParams()

    def run_gui():
        if runner_params.app_shall_exit:
            state.app_ask_exit()
        gui(state)
        runner_params.app_shall_exit = not state.app_is_runnning

    def callback_load_font():
        io = imgui.get_io()
        io.fonts.add_font_from_file_ttf(
            path.join(thisdir, "fonts", "JuliaMono-Regular.ttf"),
            args.font_size,
            None,
            io.fonts.get_glyph_ranges_vietnamese(),
        )

    def on_exit():
        import sys
        sys.exit(0)

    runner_params.callbacks.load_additional_fonts = callback_load_font
    runner_params.callbacks.show_gui = run_gui
    runner_params.callbacks.before_exit = on_exit
    # runner_params.callbacks.show_menus = lambda: draw_menu_bar(state)
    # runner_params.imgui_window_params.default_imgui_window_type = imgui.Def
    add_ons_params = immapp.AddOnsParams(with_node_editor=True, with_markdown=True)
    
    immapp.run(runner_params, add_ons_params)


if __name__ == "__main__":
    main()
