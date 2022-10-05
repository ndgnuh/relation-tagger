from itertools import starmap
from multiprocessing.dummy import Pool
from typing import List, Dict
from functools import cache
import pygame_gui
import pygame

module_state: Dict = dict(buttons=[])


def kill_button(btn):
    btn.kill()


@cache
def draw(state):
    current_data = state.current_data.get()
    if current_data is None:
        return

    manager = state.ui.manager.get()
    with Pool(16) as p:
        p.map(kill_button, module_state["buttons"])

    ww, wh = state.ui.window_size.get()
    boxes = current_data['boxes_normalized'] * 1.0
    boxes[[0, 2]] *= ww
    boxes[[1, 3]] *= ww
    boxes = boxes.round().astype(int).T
    texts = current_data['texts']
    n = len(texts)

    # Map selection
    selection = state.selection.get()
    is_selected = [False] * n
    for i in selection:
        is_selected[i] = True

    # indices
    indices = list(range(n))

    def draw_button(box, text, idx, is_selected):
        x1, y1, x2, y2 = box
        rect = pygame.Rect(x1, y1, x2 - x1, y2 - y1)
        btn = pygame_gui.elements.UIButton(relative_rect=rect,
                                           text=text,
                                           manager=manager)
        btn.id = "dynamic/textbox"
        btn.index = idx
        if idx in selection:
            btn.select()
        return btn

    buttons = starmap(draw_button, zip(boxes, texts, indices, is_selected))
    module_state["buttons"] = list(buttons)

    # for i, (box, text) in enumerate(zip(boxes, texts)):

    #     x1, y1, x2, y2 = box
    #     rect = pygame.Rect(x1, y1, x2 - x1, y2 - y1)
    #     btn = pygame_gui.elements.UIButton(relative_rect=rect,
    #                                        text=text,
    #                                        manager=manager)
    #     btn.id = "dynamic/textbox"
    #     btn.index = i
    #     if i in selection:
    #         btn.select()
    #     buttons.append(btn)
