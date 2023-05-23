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
        self.value = self.value if value is None else value
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


def EventField():
    return field(default_factory=Event)


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

    node_editor_add_links: Event = EventField()
    node_editor_remove_links: Event = EventField()
    node_editor_reinit: Event = EventField()
    node_editor_copy_text: Event = EventField()

    # Command palette states
    command_palette_show: Event = EventField()
    command_palette_options: Event = EventField()
    command_palette_selected_idx: Event = EventField()

    # dataset states
    dataset: Optional[Dataset] = None
    dataset_pick_file: Event[bool] = EventField()
    dataset_save_file: Event[str] = EventField()
    dataset_export_file: Event[str] = EventField()
    dataset_ask_pick_file: Event[bool] = EventField()
    dataset_ask_import_file: Event[bool] = EventField()
    dataset_ask_export_file: Event[bool] = EventField()
    dataset_ask_export_file_confirm: Event[bool] = EventField()
    dataset_ask_assign_class: Event[int] = EventField()
    dataset_ask_delete_sample: Event = EventField()
    dataset_delete_sample: Event = EventField()
    dataset_next: Event = EventField()
    dataset_previous: Event = EventField()
    dataset_jump_to: Event = EventField()
    dataset_toggle_preview: Event = EventField()
    dataset_ask_export_file: Event = EventField()

    # App state
    app_is_runnning: bool = True
    app_is_processing: Optional[str] = None
    app_menubar_height: int = 10
    app_shortcuts_enabled: bool = True
    show_image_preview: bool = True
    show_data_picker: bool = False
    app_function_not_implemented: Event = EventField()
    app_ask_exit: Event = EventField()

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

        if self.dataset_ask_assign_class:
            class_idx = self.dataset_ask_assign_class.value
            print(class_idx, self.dataset_ask_assign_class)
            for node in self.node_editor_selections:
                self.dataset.set_text_class(node.id, class_idx)

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
