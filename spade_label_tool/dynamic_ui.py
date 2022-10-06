from dataclasses import dataclass, field
from typing import Dict, Any, Tuple, List
from functools import cache, lru_cache
from spade_label_tool.utils import memoize, get_rect
from spade_label_tool.utils.edges import find_endpoints
import pygame_gui
import pygame
import numpy as np

module_state: Dict = dict(buttons=[])


def format_text(s):
    return f"<font face='sans'>{s}</font>"


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

    # @memoize(maxsize=1)
    def draw_current_data_edge(self, current_data):
        if current_data is None:
            return

        edge_index = current_data['edge_index']
        buttons = self.refs['data_buttons']
        for i, j in edge_index:
            btn1 = buttons[i]
            btn2 = buttons[j]
            if not btn1.visible or not btn2.visible:
                continue
            box1 = btn1.relative_rect
            box2 = btn2.relative_rect
            p1, p2 = find_endpoints(box1, box2)
            pygame.draw.line(self.root, (255, 255, 255), p1, p2, 2)

    @memoize()
    def get_display_position(self,
                             boxes: np.ndarray,
                             width: int,
                             height: int,
                             scroll_x: int,
                             scroll_y: int,
                             zoom_factor: float):
        boxes[[0, 2]] *= width
        boxes[[1, 3]] *= width

        min_height = zoom_factor
        current_min_height = (boxes[3] - boxes[1]).min()
        if min_height > current_min_height:
            ratio = min_height / current_min_height
            boxes[[0, 2]] *= ratio
            boxes[[1, 3]] *= ratio
        boxes = boxes.round().astype(int).T

        scroll_offset = np.array(
            [scroll_x, scroll_y, scroll_x, scroll_y], dtype=int)

        boxes = boxes + scroll_offset[None, :]
        return boxes

    @memoize(maxsize=1)
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

        # print("Redraw", current_data['edge_index'])
        self.clear()

        boxes = self.get_display_position(
            current_data['boxes_normalized'] * 1.0,
            width,
            height,
            scroll_x,
            scroll_y,
            zoom_factor)
        texts = current_data['texts']

        buttons = []
        for i, (box, text) in enumerate(zip(boxes, texts)):

            x1, y1, x2, y2 = box
            rect = pygame.Rect(x1, y1, x2 - x1, y2 - y1)
            # text = format_text(text)
            btn = pygame_gui.elements.UIButton(relative_rect=rect,
                                               object_id="#text-node",
                                               text=text,
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
        self.draw_current_data_edge(state.current_data.get())
