import copy
import json
import traceback
from dataclasses import dataclass, field
from functools import lru_cache, wraps
from typing import *
from threading import Thread

from .data import Dataset
from .utils import reactive_class, reactive, requires

T = TypeVar("T")


@dataclass
class Event(Generic[T]):
    trigger: bool = False
    value: Optional[T] = None

    def set(self, value: T = None):
        self.value = value or self.value
        self.trigger = True
        return self

    def get(self):
        return self.value

    def check(self):
        ret = (self.trigger, self.value)
        if self.trigger:
            self.trigger = False
        return ret

    # Convenience-s + compat
    def __call__(self, value=True):
        return self.set(value)

    def __bool__(self):
        return self.check()[0]


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
    dataset_pick_file: Event[bool] = Event()
    dataset_save_file: Event[str] = Event()
    dataset_export_file: Event[str] = Event()
    dataset_ask_pick_file: Event[bool] = Event()
    dataset_ask_import_file: Event[bool] = Event()
    dataset_ask_export_file: Event[bool] = Event()
    dataset_ask_export_file_confirm: Event[bool] = Event()
    dataset_ask_delete_sample: Event = Event()
    dataset_delete_sample: Event = Event()
    dataset_next: Event = Event()
    dataset_previous: Event = Event()
    dataset_jump_to: Event = Event()
    dataset_toggle_preview: Event = Event()
    dataset_ask_export_file: Event = Event()

    # App state
    app_is_runnning: bool = True
    app_is_processing: Optional[str] = None
    app_menubar_height: int = 10
    app_shortcuts_enabled: bool = True
    show_image_preview: bool = True
    show_data_picker: bool = False
    app_function_not_implemented: Event = Event()
    app_ask_exit: Event = Event()

    def _process(self, message, function, *args, **kwargs):
        def callback():
            self.app_is_processing = message
            function(*args, **kwargs)
            self.app_is_processing = None

        Thread(target=callback).start()

    def _load_data(self):
        self.dataset = Dataset.from_file(self.dataset_pick_file.value)

    def _export_data(self):
        self.dataset.save_minified(self.dataset_export_file.value)

    def handle(self):
        # TODO: sugar coat this thing, add a mapping table or something like that
        if self.dataset_save_file:
            self._process("Saving dataset", self.dataset.save)

        if self.dataset_pick_file:
            self._process("Loading dataset", self._load_data)

        if self.dataset_previous:
            self.dataset and self.dataset.previous_data()

        if self.dataset_jump_to:
            self.dataset and self.dataset.jump_to(self.dataset_jump_to.value)

        if self.dataset_next:
            self.dataset and self.dataset.next_data()

        if self.dataset_toggle_preview:
            self.show_image_preview = not self.show_image_preview

        if self.dataset_delete_sample:
            self.dataset and self.dataset.delete_current_sample()

        if self.dataset_export_file:
            self._process("Exporting dataset", self._export_data)

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
