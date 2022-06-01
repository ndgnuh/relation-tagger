# Handle states + dynamic UI
import pygame as pg
import pygame_gui as pgui
from lenses import lens, bind
from dataclasses import dataclass
from typing import Optional, Dict, List, Callable


@dataclass(frozen=True, eq=True)
class UI:
    manager: any = None
    filepicker_labelfile: any = None
    filepicker_datafile: any = None


@dataclass
class Data:
    labels: Optional[List[str]] = None


@dataclass(frozen=True, eq=True)
class State:
    data: Data = Data()
    data_index: int = 1
    is_running: bool = True
    ui: UI = UI()


def create_state():
    state = State(data=Data())
    return bind(state)


def stop(state):
    state = state.is_running.set(False)
    return bind(state)


def read_data(state, path):
    return state


def load_labels(state, labelfile):
    with open(labelfile) as f:
        labels = f.readlines()
        labels = [label.strip() for label in labels]
        labels = [label for label in labels
                  if len(label) > 0]
    state = state.data.labels.set(labels)
    return bind(state)


def create_ui_manager(state, root):
    manager = pgui.UIManager(root.get_size())
    state = state.ui.manager.set(manager)
    return bind(state)


def pickfile(state, name):
    attr = f'filepicker_{name}'
    picker = pgui.windows.UIFileDialog(
        rect=pg.Rect(0, 0, 400, 400),
        manager=state.ui.manager.get())
    state = state.ui.GetAttr(attr).set(picker)
    return bind(state)
