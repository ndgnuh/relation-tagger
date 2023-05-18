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
    dataset_ask_pick_file: Event[bool] = Event()
    dataset_pick_file: Event[bool] = Event()
    dataset_save_file: Event[str] = Event()
    dataset_ask_delete_sample: Event = Event()
    dataset_delete_sample: Event = Event()
    dataset_next: Event = Event()
    dataset_previous: Event = Event()
    dataset_jump: Event = Event()
    dataset_toggle_preview: Event = Event()

    app_wants_exit: bool = False
    app_is_runnning: bool = True
    app_menubar_height: int = 10
    app_shortcuts_enabled: bool = True
    show_image_preview: bool = True
    show_data_picker: bool = False

    def handle(self):
        # TODO: sugar coat this thing, add a mapping table or something like that
        if self.dataset_save_file:
            self.dataset.save()

        if self.dataset_pick_file:
            self.dataset = Dataset.from_file(self.dataset_pick_file.value)

        if self.dataset_previous:
            self.dataset and self.dataset.previous_data()

        if self.dataset_next:
            self.dataset and self.dataset.next_data()

        if self.dataset_toggle_preview:
            self.show_image_preview = not self.show_image_preview
        
        if self.dataset_delete_sample:
            self.dataset and self.dataset.delete_current_sample()

        # Guard if any event is NOT handled
        # unhandled = []
        # for k, v in vars(self).items():
        #     if isinstance(v, Event):
        #         if v:
        #             unhandled.append(v)
        # print(unhandled)
        # assert len(unhandled) == 0

    def resolve_error(self):
        raise RuntimeError("We are supposed to override this function in runtime???")

    def throw_error(self, msg, **resolve_states):
        def resolve():
            for k, v in resolve_states.items():
                setattr(self, k, v)
            self.error = None

        self.error = msg
        self.resolve_error = resolve


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
