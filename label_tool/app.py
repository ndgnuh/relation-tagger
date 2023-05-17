import random
from os import path
from itertools import product
from dataclasses import dataclass
from imgui_bundle import imgui, immapp, hello_imgui
from imgui_bundle import im_file_dialog as fd
from .widgets.filepicker import pick_open_file
from .states import State
from .widgets.node_editor import NodeEditor, node_editor
from .widgets import filepicker
from .widgets.dirty_indicator import dirty_indicator, save_button
from .widgets.data_widgets import label_selector
from .widgets import (
    data_widgets as dw,
    modals
)
from .widgets.menubar import draw_menu_bar
from .shortcuts import Shortcut

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
        imgui.menu_item("Show shortcuts", "Ctrl+/", False, True)
        imgui.text_wrapped("(This functionality is not implemented)")
        imgui.end_group()
        imgui.bullet()
        if imgui.menu_item("Toggle thumbnail", "Tab", False, True)[0]:
            state.toggle_show_image_preview()

        imgui.bullet()
        if imgui.menu_item("Debug", "", False, True)[0]:
            if imgui.begin_popup("Debug", imgui.WindowFlags_.popup):
                imgui.text("Hello")
            imgui.end_popup()

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
        # if state.node_editor is not None:
        #     imgui.same_line()
        #     state.node_editor.on_frame()
        # End second panel
        imgui.end()


        # handle shortcut
        Shortcut.on_frame(state)

        # Conditional widgets/popups
        # Must be drawn last
        dataset_file = filepicker.pick_open_file(state)
        if dataset_file is not None:
            state.dataset_file = dataset_file
            state.dataset # trigger the dataset loading?

        # Modal to warn on exit
        # it still quits after the dataset is saved
        if state.app_wants_exit:
            state.app_is_runnning = modals.warn_on_exit(state)

        if state.app_wants_save_data:
            state.data.save()
            state.app_wants_save_data = False
    except Exception as e:
        import traceback

        traceback.print_exc()
        state.error = str(e)


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
    state.dataset_file = args.data
    runner_params = immapp.RunnerParams()

    def run_gui():
        state.app_wants_exit = runner_params.app_shall_exit
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
    # runner_params.imgui_window_params.show_menu_bar = True
    # runner_params.imgui_window_params.enable_viewports = True
    add_ons_params = immapp.AddOnsParams(with_node_editor=True, with_markdown=True)
    
    immapp.run(runner_params, add_ons_params)


if __name__ == "__main__":
    main()
