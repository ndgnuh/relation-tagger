from spade_label_tool.utils import Functables
from lenses import bind
import pygame

callbacks = Functables()


def change_data_index(state, delta: int):
    data = state.data.get()
    if data is None:
        return state

    data_index = state.data_index.get()
    data_index = data_index + delta
    data_index = max(data_index, 0)
    data_index = min(data_index, len(data) - 1)
    print(state.data_index.get(), '->', data_index)
    state = bind(state.data_index.set(data_index))

    return state


@callbacks(pygame.K_a)
def prev_index(event, state):
    return change_data_index(state, -1)


@callbacks(pygame.K_d)
def next_index(event, state):
    return change_data_index(state, 1)


print(callbacks)


def handle_keyboard(event, state):
    print(event)
    f = callbacks.get(event.key, None)
    if f is None:
        return state
    print("f is", f)

    return f(event, state)
