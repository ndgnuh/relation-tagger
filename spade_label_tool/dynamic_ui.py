from dataclasses import dataclass, field
from typing import Dict, Any, Tuple, List
from functools import cache
import pygame_gui
import pygame

module_state: Dict = dict(buttons=[])


@dataclass
class DrawContext(dict):
    root: Any
    manager: Any
    buttons: List = field(default_factory=list)

    def draw_selection_region(self, region):
        if region is None:
            return

        pygame.draw.rect(self.root,
                         pygame.Color(255, 255, 255, 30),
                         region)

    def __hash__(self):
        return id(self)

    @cache
    def draw_current_data(self,
                          current_data,
                          selection,
                          width: int,
                          height: int):
        if current_data is None:
            return

        for btn in self.buttons:
            btn.kill()
        self.buttons = []

        boxes = current_data.boxes_normalized * 1.0
        boxes[[0, 2]] *= width
        boxes[[1, 3]] *= width
        boxes = boxes.round().astype(int).T
        texts = current_data.texts
        print(selection)
        for i, (box, text) in enumerate(zip(boxes, texts)):

            x1, y1, x2, y2 = box
            rect = pygame.Rect(x1, y1, x2 - x1, y2 - y1)
            btn = pygame_gui.elements.UIButton(relative_rect=rect,
                                               text=text,
                                               manager=self.manager)
            btn.id = "dynamic/textbox"
            btn.index = i
            if i in selection:
                btn.select()
            self.buttons.append(btn)

        # print(buttons)

    def draw(self, state):
        self.draw_selection_region(state.ui_selection_region.get())
        self.draw_current_data(
            state.current_data.get(),
            state.selection.get(),
            *state.ui.window_size.get())
