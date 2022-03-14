import pyperclip
from dataclasses import dataclass, field, fields
import pandas as pd
from typing import Union, List, Callable, Optional
import custom_events as ce
from metadata import Label, Token, Graph
import pickle
from ast import literal_eval
import numpy as np

REL_S_KEY = 'graph_s'
REL_G_KEY = 'graph_g'


class Reactive:
    DEFAULT_CBS: list = []
    callbacks: dict = {}

    def __init__(self):
        self.__dict__['callbacks'] = {}

    def __setattr__(self, name, value):
        old = getattr(self, name, None)
        self.__dict__[name] = value
        for cb in self.__class__.callbacks.get(name, Reactive.DEFAULT_CBS):
            cb(self, old, value)

    def rawset(self, name, value):
        self.__dict__[name] = value

    @classmethod
    def connect(cls, signals, cb=None):
        if isinstance(signals, str):
            signals = [signals]

        # Create if not exists
        for signal in signals:
            if signal not in cls.callbacks:
                cls.callbacks[signal] = []

        # RET
        if cb is None:
            def reg(callback):
                for signal in signals:
                    cls.callbacks[signal].append(callback)
            return reg
        else:
            for signal in signals:
                cls.callbacks[signal].append(cb)
            return cb


def no_new_field(cls):
    oldsetatttr = cls.__setattr__

    def __setattr__(self, key, value):
        keys = [f.name for f in fields(self)]
        msg = f'No key {key}, list of available keys: {keys}'
        assert key in keys, msg
        oldsetatttr(self, key, value)

    cls.__setattr__ = __setattr__
    return cls


@no_new_field
@dataclass
class State(Reactive):
    data: Optional[pd.DataFrame] = None
    data_index: int = 0
    imgdir: Optional[str] = None
    labelfile: Optional[str] = None
    labels: Optional[List[str]] = None
    labels_rs: List[str] = field(default_factory=list)
    rel_s: List = field(default_factory=list)
    rel_g: List = field(default_factory=list)
    selection: List = field(default_factory=list)
    # UI
    mainview_y_offset: int = 50
    mainview_x_offset: int = 50
    sidebar_y_offset: int = 0
    sidebar_y_spacing: int = 1


eh = ce.EventHandler()
process_event = eh.process_event


@State.connect("data_index")
def _(state, *args):
    if state.data is not None:
        return
        # df = state.data
        # try:
        #     pass
        #     print(df[REL_S_KEY][state.data_index])
        # except Exception as e:
        #     print(type(e), e)
        #     pass
    ce.emit(ce.SUCCESS_CHANGE_DATAINDEX, now=True)


@State.connect("labels_rs")
def _(state, *args):
    if state.labels is not None:
        return

    for label in state.labels_rs:
        if label not in state.labels:
            state.labels_rs.remove(label)

    # print(state.labels_rs)


@State.connect(["data", "labels"])
def build_graph(state, *args):
    if state.data is None or state.labels is None:
        # print(state.data, state.labels)
        return
    df = state.data
    labels = state.labels

    def graph(row, kind):
        texts = list(row['img_texts'])
        bboxes = list(row['img_bboxes'])
        bboxes = ['-'.join([str(i) for i in b]) for b in bboxes]

        if kind in row:
            adj = row[kind]
            adj = np.array(adj)
        else:
            adj = None
        g = Graph(texts=texts, labels=labels, bboxes=bboxes, adj=adj)
        return g

    if REL_S_KEY not in state.data.columns:
        g = df.apply(
            lambda row: graph(row, 'rel_s'), axis=1)
        state.data[REL_S_KEY] = g
    if REL_G_KEY not in state.data.columns:
        state.data[REL_G_KEY] = df.apply(
            lambda row: graph(row, 'rel_g'), axis=1)


@eh.register(ce.ACTION_CHANGE_DATAINDEX)
def change_data_index(event, state):
    if state.data is None:
        return

    n, _ = state.data.shape
    i = state.data_index
    i = i + event.offset
    i = max(min(i, n-1), 0)
    state.data_index = i
    state.mainview_x_offset = 50
    state.mainview_y_offset = 50


@eh.register(ce.SUCCESS_IMPORT_LABELS)
def change_label(event, state):
    state.labels = event.labels
    if hasattr(event, 'labels_rs'):
        labels_rs = event.labels_rs
    else:
        labels_rs = state.labels_rs

    state.labels_rs = [label for label in labels_rs
                       if label in state.labels]

    for (i, row) in state.data.iterrows():
        state.data.loc[i, REL_S_KEY].update_labels(event.labels)
        state.data.loc[i, REL_G_KEY].update_labels(event.labels)


@eh.register(ce.SUCCESS_IMPORT_DATA)
def change_data(event, state):
    state.data = event.data
    state.data_index = 0


@eh.register(ce.SUCCESS_SELECT_IMGDIR)
def change_imgdir(event, state):
    state.imgdir = event.imgdir


@eh.register(ce.ACTION_REL_S)
def toggle_rel_s(event, state):
    if state.data is None:
        return

    rel = state.data.loc[state.data_index, REL_S_KEY]
    selection = event.selection.copy()
    if len(selection) < 2:
        ce.emit(ce.SUCCESS_REL_S, now=True)
        return

    if event.fanout:
        try:
            b1 = selection.pop(0)
            for b2 in selection:
                rel.toggle_edge(b1.meta, b2.meta)
        except Exception:
            print(f"Can't add edge {b1}, {b2}")
    else:
        for (b1, b2) in zip(selection, selection[1:]):
            try:
                rel.toggle_edge(b1.meta, b2.meta)
            except Exception:
                print(f"Can't add edge {b1}, {b2}")

    ce.emit(ce.SUCCESS_REL_S, now=True)


@eh.register(ce.ACTION_REL_G)
def toggle_rel_g(event, state):
    if state.data is None:
        return

    rel = state.data.loc[state.data_index, REL_G_KEY]
    selection = event.selection.copy()
    b1 = selection.pop(0)
    for b2 in selection:
        try:
            rel.toggle_edge(b1.meta, b2.meta)
        except Exception:
            print(f"Can't add edge {b1}, {b2}")

    ce.emit(ce.SUCCESS_REL_G, now=True)


@eh.register(ce.ACTION_REL_REMOVE)
def remove_rel(event, state):
    if state.data is None:
        return

    rel_s = state.data.loc[state.data_index, REL_S_KEY]
    rel_g = state.data.loc[state.data_index, REL_G_KEY]
    selection = event.selection.copy()

    for i in selection:
        i = i.meta
        for j in selection:
            j = j.meta
            rel_s.remove_edge(i, j)
            rel_s.remove_edge(j, i)
            rel_g.remove_edge(i, j)
            rel_g.remove_edge(j, i)

    ce.emit(ce.SUCCESS_REL_REMOVE, now=True)


@eh.register(ce.ACTION_SAVE_SESSION)
def save_session(event, state):
    ce.emit(ce.REQUEST_SAVE_SESSION, state=state, now=True)


@eh.register(ce.REQUEST_LOAD_SESSION)
def load_session(event, state):
    for key in state.__dict__:
        if hasattr(event.state, key):
            val = getattr(event.state, key)
            setattr(state, key, val)


@eh.register(ce.ACTION_LABEL_RS)
def set_field_rs(event, state):
    field_rs = state.labels_rs
    for b in event.selection:
        m = b.meta
        if not isinstance(m, Label):
            continue

        m = m.text
        if m in field_rs:
            field_rs.remove(m)
        else:
            field_rs.append(m)

    # print(state.labels_rs)
    ce.emit(ce.SUCCESS_LABEL_RS, now=True)


@eh.register(ce.ACTION_DELETE_RECORD)
def delete_record(event, state):
    df = state.data.drop([state.data_index], axis=0)
    # If I drop 1, Pandas keep index as 0, 2, 3, 4... lol
    df = df.reset_index(drop=True)

    # Because python
    state.data = df

    ce.emit(ce.ACTION_CHANGE_DATAINDEX, offset=0, now=True)


@eh.register(ce.ACTION_COPY)
def copy_text(event, state):
    texts = [b.text for b in event.selection]
    texts = ' '.join(texts)
    pyperclip.copy(texts)
    ce.emit(ce.SUCCESS_REL_S, now=True)
