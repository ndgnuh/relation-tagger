import copy
import json
from dataclasses import dataclass, field
from functools import lru_cache, wraps
from typing import *

from .data import Dataset
from .utils import reactive_class, reactive, requires


@reactive_class
@dataclass
class State:
    error: Optional[str] = None
    dataset_file: Optional[str] = None
    previous: Optional = None

    # node editor states
    node_editor_nodes: Optional[List] = field(default_factory=list)
    node_editor_links: Optional[List] = field(default_factory=list)
    node_editor_selections: Optional[List] = field(default_factory=list)
    node_editor_add_links: bool = False
    node_editor_remove_links: bool = False
    node_editor_reinit: bool = False

    # Command palette states
    command_palette_show: bool = False
    command_palette_options: Optional[List] = None
    command_palette_selected_idx: Optional[int] = None

    # inferable
    dataset: Optional[Dataset] = None

    app_wants_exit: bool = False
    app_is_runnning: bool = True
    app_wants_save_data: bool = False
    app_menubar_height: int = 10
    app_shortcuts_enabled: bool = True
    show_image_preview: bool = True
    show_data_picker: bool = False

    def toggle_show_image_preview(self):
        self.show_image_preview = not self.show_image_preview

    def checkpoint(self):
        self.previous = copy.copy(self)

    def resolve_error(self):
        for k, v in vars(state.previous).items():
            setattr(self, k, v)

    def throw_error(self, msg, **resolve_states):
        def resolve():
            for k, v in resolve_states.items():
                setattr(self, k, v)
            self.error = None

        self.error = msg
        self.resolve_error = resolve


@reactive(State, "dataset_file")
def dataset(self, dataset_file):
    if dataset_file is None:
        return None
    try:
        with open(dataset_file, "r") as fp:
            data = json.load(fp)
            data["path"] = dataset_file
        self.dataset = Dataset.from_dict(data)
    except Exception as e:
        self.throw_error(str(e), dataset_file=None)
