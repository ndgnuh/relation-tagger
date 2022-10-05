from spade_label_tool.utils import Functables
from typing import Dict, List
import pygame
from lenses import bind

callbacks = Functables()
actions: List = [pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN]
mouse_buttons: List = [
    pygame.BUTTON_RIGHT,
    pygame.BUTTON_LEFT,
    pygame.BUTTON_WHEELDOWN,
    pygame.BUTTON_WHEELUP
]
mouse_state: Dict = dict(pressed=dict())
for button in mouse_buttons:
    mouse_state['pressed'][button] = False


@callbacks((pygame.MOUSEBUTTONDOWN, pygame.BUTTON_LEFT))
def maybe_start_selection(event, state):
    x, y = event.pos
    state = bind(state.ui_selection_region.set(pygame.Rect(x, y, 0, 0)))
    mouse_state['start'] = x, y
    return state


@callbacks(pygame.MOUSEMOTION)
def move_selection(event, state):
    region = state.ui_selection_region.get()
    if region is None:
        return state

    x1, y1 = mouse_state['start']
    x2, y2 = event.pos
    xs = (x1, x2)
    ys = (y1, y2)
    x1, x2 = min(xs), max(xs)
    y1, y2 = min(ys), max(ys)
    w = x2 - x1
    h = y2 - y1
    if w > 10 and h > 10:
        state = bind(state.ui_selection_region.set(
            pygame.Rect(x1, y1, w, h)))
    return state


@callbacks((pygame.MOUSEBUTTONUP, pygame.BUTTON_LEFT))
def select_region(event, state):
    manager = state.ui.manager.get()
    region = state.ui_selection_region.get()
    selection = state.selection.get()

    buttons = manager.root_container.elements
    rects = [(getattr(btn, 'index', None), btn.rect) for btn in buttons]
    new_selection = [i for (i, rect) in rects
                     if pygame.Rect.colliderect(rect, region)
                     and i is not None]
    selection = (*selection, *new_selection)
    selection = tuple(set(selection))

    state = bind(state.ui_selection_region.set(None))
    state = bind(state.selection.set(selection))
    return state


@callbacks((pygame.MOUSEBUTTONUP, pygame.BUTTON_RIGHT))
def clear_region(event, state):
    state = bind(state.selection.set(tuple()))
    return state


def handle_mouse(event, state):
    if event.type == pygame.MOUSEMOTION:
        callback = callbacks.get(event.type, None)
    else:
        callback = callbacks.get((event.type, event.button), None)
    if callback is None:
        return state

    state = callback(event, state)
    return state
