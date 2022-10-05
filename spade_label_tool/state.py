# Handle states + dynamic UI
import pygame as pg
import pygame_gui as pgui
from lenses import lens, bind
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Callable
import json
from functools import cached_property


@dataclass(frozen=True, eq=True)
class UI:
    manager: any = None
    window_width: int = 600
    window_height: int = 600

    @property
    def window_size(self):
        return self.window_width, self.window_height


@dataclass(frozen=True, eq=True)
class State:
    selection: List[Dict] = field(default_factory=list)
    data: Optional[List[Dict]] = None
    data_index: int = 1
    is_running: bool = True
    ui: UI = UI()

    @property
    def current_data(self):
        if self.data is None:
            return None
        else:
            return self.data[self.data_index]


def setui(focus, ui):
    def kill_recursively(elems):
        if elems is None:
            return
        elif isinstance(elems, list):
            for e in elems:
                kill_recursively(e)
        elif hasattr(elems, "kill"):
            elems.kill()
    kill_recursively(focus.get())
    return focus.set(ui)


def create_state():
    state = State()
    return bind(state)


def stop(state):
    state = state.is_running.set(False)
    return bind(state)


def read_data(state, path):
    return state


def load_data(state, datafile):
    with open(datafile) as f:
        data = [json.loads(line) for line in f.readlines()]

    # Empty data
    if len(data) == 0:
        return state

    # Data state
    texts = [d['text'] for d in data]
    bboxes = [d['coord'] for d in data]
    state = bind(state.data.texts.set(texts))
    state = bind(state.data.bboxes.set(bboxes))
    state = bind(state.data.dataindex.set(0))

    # UI state
    manager = state.ui.manager.get()
    cbboxes = bboxes[0]
    ctexts = texts[0]
    buttons = []
    for (text, bbox) in zip(ctexts, cbboxes):
        tl, tr, br, bl = bbox
        x1, y1 = tl
        x2, y2 = br
        button = pgui.elements.UIButton(
            relative_rect=pg.Rect(x1, y1, x2 - x1, y2 - y1),
            text=text,
            manager=manager
        )
        buttons.append(button)
    state = setui(state.ui.button_texts, buttons)
    state = bind(state)
    return state


def load_labels(state, labelfile):
    with open(labelfile) as f:
        labels = f.readlines()
        labels = [label.strip() for label in labels]
        labels = [label for label in labels
                  if len(label) > 0]
    # Label data
    state = bind(state.data.labels.set(labels))

    # Label UI buttons
    buttons = []
    y = 50
    height = 50
    manager = state.ui.manager.get()
    for label in labels:
        button = pgui.elements.UIButton(
            relative_rect=pg.Rect(0, y, 200, height),
            text=label,
            manager=manager)
        y = y + height
        buttons.append(button)
    state = setui(state.ui.button_labels, buttons)
    state = bind(state)
    return state


def create_ui_manager(state, root):
    manager = pgui.UIManager(root.get_size())
    state = state.ui.manager.set(manager)
    return bind(state)


def pickfile(state, name):
    attr = f'filepicker_{name}'
    # old_picker = state.ui.GetAttr(attr).get()
    # if old_picker is not None:
    #     old_picker.kill()
    # print(old_picker)
    picker = pgui.windows.UIFileDialog(
        rect=pg.Rect(0, 0, 400, 400),
        manager=state.ui.manager.get())
    state = setui(state.ui.GetAttr(attr), picker)
    return bind(state)
