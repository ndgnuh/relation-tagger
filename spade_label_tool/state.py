from lenses import lens, bind
from dataclasses import dataclass
from typing import Optional, Dict, List, Callable


@dataclass(frozen=True, eq=True)
class State:
    data: Optional[Dict]
    data_index: int = 1
    is_running: bool = True


def create_state():
    state = State(data=None)
    return bind(state)


def stop(state):
    state = state.is_running.set(False)
    return bind(state)


def read_data(state, path):
    return state
