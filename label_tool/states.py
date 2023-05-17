import copy
import json
from dataclasses import dataclass
from functools import lru_cache, wraps
from typing import *

from .widgets.node_editor import NodeEditor
from .data import Dataset


def requires(fields):
    if isinstance(fields, str):
        fields = [fields]

    def wrapper(f):
        @wraps(f)
        def wrapped(state, *args, **kwargs):
            for k in fields:
                if getattr(state, k, None) is None:
                    return
            f(state, *args, **kwargs)

        return wrapped

    return wrapper


@lru_cache
def read_data(dataset_file: str) -> Dataset:
    with open(dataset_file, "r") as fp:
        data = json.load(fp)
        data["path"] = dataset_file
    return Dataset.from_dict(data)


@lru_cache
def create_node_editor(dataset: Dataset):
    if dataset is None:
        return
    sample = dataset.get_current_sample()
    boxes = dataset.get_current_centers()
    return NodeEditor(dataset)


def toggle(x):
    print(x)
    return x


@dataclass
class State:
    error: Optional[str] = None
    dataset_file: Optional[str] = None
    previous: Optional = None

    app_wants_exit: bool = False
    app_is_runnning: bool = True
    show_image_preview: bool = True
    show_data_picker: bool = True

    def toggle_show_image_preview(self):
        self.show_image_preview = not self.show_image_preview

    def checkpoint(self):
        self.previous = copy.copy(self)

    def resolve_error(self):
        for k, v in vars(state.previous).items():
            setattr(self, k, v)

    @property
    def node_editor(self):
        return create_node_editor(self.dataset)

    @property
    def dataset(self):
        if self.dataset_file is None:
            return None
        try:
            return read_data(self.dataset_file)
        except Exception as e:
            self.throw_error(str(e), dataset_file=None)

    def throw_error(self, msg, **resolve_states):
        def resolve():
            for k, v in resolve_states.items():
                setattr(self, k, v)
            self.error = None

        self.error = msg
        self.resolve_error = resolve
