from spade_label_tool.utils import Functables
from lenses import bind
import pygame
from itertools import product
from spade_label_tool import features

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


@callbacks(pygame.K_s)
def key_s(event, state):
    if pygame.key.get_mods() & pygame.KMOD_CTRL:
        return features.init_save_file(event, state)
    return state


@callbacks(pygame.K_o)
def key_o(event, state):
    if pygame.key.get_mods() & pygame.KMOD_CTRL:
        return features.init_load_file(event, state)
    return state


@callbacks(pygame.K_r)
def clear_edges(event, state):
    data_index = state.data_index.get()
    selection = state.selection.get()
    edge_index = state.current_data['edge_index'].get()
    if edge_index is None:
        return state

    if len(selection) == 0:
        return state
    if event.mod & pygame.KMOD_SHIFT:
        # Clear all
        edge_index = [(i, j) for (i, j) in edge_index
                      if i not in selection and j not in selection]
    else:
        edge_index = set(edge_index)  # use set to remove without error
        for i, j in zip(selection, selection[1:]):
            edge_index.discard((i, j))
            edge_index.discard((j, i))
    edge_index = tuple(edge_index)

    state = bind(state.data[data_index]['edge_index'].set(edge_index))
    state = bind(state.selection.set(tuple()))
    return state


@callbacks(pygame.K_SPACE)
def add_edges(event, state):
    data_index = state.data_index.get()
    selection = state.selection.get()
    edge_index = state.current_data['edge_index'].get()
    if edge_index is None:
        return state

    if len(selection) == 0:
        return state

    new_edge_index = [e for e in zip(selection, selection[1:])
                      if e not in edge_index]
    rem_edge_index = [e for e in zip(selection, selection[1:])
                      if e in edge_index]

    edge_index = list(edge_index) + new_edge_index
    edge_index = [e for e in edge_index if e not in rem_edge_index]
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
