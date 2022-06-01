from lenses import lens, bind
from dataclasses import dataclass
from typing import Optional, Dict, List, Callable


@dataclass(frozen=True, eq=True)
class State:
    data: Optional[Dict]
    data_index: int = 1


def create_state():
    state = State(data=None)
    return bind(state)
