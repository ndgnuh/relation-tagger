import json
from dataclasses import dataclass
from functools import lru_cache
from typing import *


@lru_cache
def read_label(dataset_file: str) -> List[str]:
    with open(dataset_file, "r") as fp:
        data = json.load(fp)


@lru_cache
def read_data(dataset_file: str) -> Dict:
    with open(dataset_file, "r") as fp:
        data = json.load(fp)
    return data


@dataclass
class State:
    resolve_error: Callable = lambda: None
    error: Optional[Error] = None
    dataset_file: Optional[str] = None

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
