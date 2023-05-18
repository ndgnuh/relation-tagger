from dataclasses import dataclass
from imgui_bundle import (
    imgui,
    hello_imgui,
    imgui_md,
    imgui_toggle,
    ImVec2,
    immapp,
    ImVec4,
    icons_fontawesome,
)
from imgui_bundle import imgui_command_palette as imcmd
from .. import shortcuts, utils
from ..states import State


def _render_cache_key(state):
    if state.dataset is None:
        return ""
    return "".join(state.dataset.classes)


@utils.static
def command_palette_init(static, state: State):
    key = _render_cache_key(state)
    # Context can only becreated once
    if static["ctx"] is None:
        static["ctx"] = imcmd.ContextWrapper()

    # Cache validation
    if static["previous_cache_key"] == key:
        return
    static["previous_cache_key"] = key

    # Remove all the previous command
    for cmd in static.get("commands", []):
        imcmd.remove_command(cmd.name)

    # Command creation
    @dataclass
    class Callback:
        idx: int

        def __call__(self):
            for node in state.node_editor_selections:
                state.dataset.set_text_class(node_idx=node.id, class_idx=self.idx)

    # Class button
    commands = []
    for idx, class_name in enumerate(["(none)"] + state.dataset.classes):
        cmd = imcmd.Command()
        cmd.name = class_name
        cmd.initial_callback = Callback(idx - 1)
        imcmd.add_command(cmd)
        commands.append(cmd)

    # Cancel button
    cancel = imcmd.Command()
    cancel.name = "(cancel)"
    imcmd.add_command(cancel)
    commands.append(cancel)

    # Store commands for later deletion
    static['commands'] = commands


def command_palette(state: State):
    if not state.command_palette_show or not state.dataset:
        state.app_shortcuts_enabled = True
        return

    # Init
    command_palette_init(state)

    state.app_shortcuts_enabled = False
    state.command_palette_show = imcmd.command_palette_window("CommandPalette", True)
