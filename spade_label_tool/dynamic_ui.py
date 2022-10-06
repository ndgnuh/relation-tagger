from dataclasses import dataclass, field
from typing import Dict, Any, Tuple, List
from functools import cache, lru_cache
import pygame_gui
import pygame
import numpy as np

module_state: Dict = dict(buttons=[])


def round_to_unit(x, n):
    return np.round(x / n) * n


@dataclass
class DrawContext(dict):
    root: Any
    manager: Any
    refs: Dict = field(default_factory=dict)

    def draw_selection_region(self, region):
        if region is None:
            return

        pygame.draw.rect(self.root,
                         pygame.Color(255, 255, 255, 30),
                         region)

    def __hash__(self):
        return id(self)

    def clear(self):
        refs = self.refs
        data_container = refs.get("data_container", None)
        if data_container:
            data_container.kill()
        for btn in refs.get("data_buttons", []):
            btn.kill()

    @lru_cache(maxsize=1)
    def draw_current_data(self,
                          current_data,
                          selection,
                          width: int,
                          height: int,
                          scroll_x: int,
                          scroll_y: int,
                          zoom_factor: int):
        if current_data is None:
            return

        self.clear()

        # container = pygame_gui.elements.UIScrollingContainer(
        #     starting_height=height,
        #     relative_rect=pygame.Rect(0, 0, width, height),
        #     manager=self.manager
        # )
        # container.set_scrollable_area_dimensions((swidth, sheight))
        boxes = current_data.boxes_normalized * 1.0
        boxes[[0, 2]] *= width
        boxes[[1, 3]] *= width

        min_height = zoom_factor
        current_min_height = (boxes[3] - boxes[1]).min()
        if min_height > current_min_height:
            ratio = min_height / current_min_height
            boxes[[0, 2]] *= ratio
            boxes[[1, 3]] *= ratio
        boxes = boxes.round().astype(int).T
        texts = current_data.texts

        buttons = []
        scroll_offset = np.array(
            [scroll_x, scroll_y, scroll_x, scroll_y], dtype=int)

        print(scroll_x, scroll_y)
        for i, (box, text) in enumerate(zip(boxes, texts)):

            x1, y1, x2, y2 = (box + scroll_offset)
            rect = pygame.Rect(x1, y1, x2 - x1, y2 - y1)
            btn = pygame_gui.elements.UIButton(relative_rect=rect,
                                               text=str(text),
                                               tool_tip_text=f"Text: `{text}`",
                                               visible=y1 >= 30,
                                               # container=container,
                                               manager=self.manager)
            btn.tool_tip_delay = 0.5
            btn.id = "dynamic/textbox"
            btn.index = i
            btn.rebuild()
            buttons.append(btn)

        for si, i in enumerate(selection):
            btn = buttons[i]
            btn.text = f"[{si}] {btn.text}"
            btn.rebuild()
            btn.select()
        self.refs['data_buttons'] = buttons

    def draw(self, state):
        self.draw_selection_region(state.ui_selection_region.get())
        self.draw_current_data(
            state.current_data.get(),
            state.selection.get(),
            state.ui.window_width.get(),
            state.ui.window_height.get(),
            state.ui_scroll_x.get(),
            state.ui_scroll_y.get(),
            state.ui_zoom_factor.get(),
        )
