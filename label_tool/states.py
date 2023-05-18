import copy
import json
import traceback
from dataclasses import dataclass, field
from functools import lru_cache, wraps
from typing import *

from .data import Dataset
from .utils import reactive_class, reactive, requires
from .events import Event


def errorable(**restore_states):
    def wrapper(f):
        @wraps(f)
        def wrapped(self, *args, **kwargs):
            try:
                return f(self, *args, **kwargs)
            except Exception as e:
                trace = traceback.format_exc()
                traceback.print_exc()
                error = str(e) + "\n" + trace
                self.throw_error(error, **restore_states)

        return wrapped

    return wrapper


@reactive_class
@dataclass
class State:
    error: Optional[str] = None
    previous: Optional = None

    # node editor states
    node_editor_nodes: Optional[List] = field(default_factory=list)
    node_editor_links: Optional[List] = field(default_factory=list)
    node_editor_selections: Optional[List] = field(default_factory=list)
    node_editor_num_class_initials: int = 1

    node_editor_add_links: Event = Event()
    node_editor_remove_links: Event = Event()
    node_editor_reinit: Event = Event()
    node_editor_copy_text: Event = Event()

    # Command palette states
    command_palette_show: Event = Event()
    command_palette_options: Event = Event()
    command_palette_selected_idx: Event = Event()

    # dataset states
    dataset: Optional[Dataset] = None
    dataset_file: Optional[str] = None
    dataset_pick_file: Event[bool] = Event()
    dataset_save_file: Event[str] = Event()
    dataset_ask_delete_sample: Event = Event()
    dataset_delete_sample: Event = Event()

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
        raise RuntimeError("We are supposed to override this function in runtime???")

    def throw_error(self, msg, **resolve_states):
        def resolve():
            for k, v in resolve_states.items():
                setattr(self, k, v)
            self.error = None

        self.error = msg
        self.resolve_error = resolve


@reactive(State, "dataset_file")
@errorable(dataset_file=None)
def dataset(self, dataset_file):
    if dataset_file is None:
        return None
    with open(dataset_file, "r") as fp:
        data = json.load(fp)
        data["path"] = dataset_file
    self.dataset = Dataset.from_dict(data)


def loop_on(ev_name):
    """
    Loop on an event with early return
    """
    def wrapper(f):
        @wraps(f)
        def wrapped(state, *args, **kwargs):
            event = getattr(state, ev_name)
            if event:
                result = f(state, *args, **kwargs)
                if result:
                    event.set()

        return wrapped

    return wrapper
