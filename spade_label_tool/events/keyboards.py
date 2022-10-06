from spade_label_tool.utils import Functables
from lenses import bind
import pygame
from itertools import product

callbacks = Functables()


def change_data_index(state, delta: int):
    data = state.data.get()
    if data is None:
        return state

    data_index = state.data_index.get()
    data_index = data_index + delta
    data_index = max(data_index, 0)
    data_index = min(data_index, len(data) - 1)
    state = bind(state.data_index.set(data_index))

    return state


@callbacks(pygame.K_a)
def prev_index(event, state):
    return change_data_index(state, -1)


@callbacks(pygame.K_SPACE)
def add_edges(event, state):
    data_index = state.data_index.get()
    selection = state.selection.get()
    edge_index = state.current_data['edge_index'].get()
    if edge_index is None:
        return state

    if len(selection) == 0:
        return state

    new_edge_index = tuple(zip(selection, selection[1:]))
    edge_index = set([*edge_index, *new_edge_index])
    edge_index = tuple(edge_index)
    state = bind(state.data[data_index]['edge_index'].set(edge_index))
    state = bind(state.selection.set(tuple()))
    return state


@callbacks(pygame.K_d)
def next_index(event, state):
    return change_data_index(state, 1)


def handle_keyboard(event, state):
    f = callbacks.get(event.key, None)
    if f is None:
        return state

    return f(event, state)
