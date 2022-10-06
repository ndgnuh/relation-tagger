# Handle states + dynamic UI
import pygame as pg
import pygame_gui as pgui
import json
import pygame_gui
import pygame
from lenses import lens, bind
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Callable, Tuple
from functools import cached_property


@dataclass(frozen=True, eq=True)
class State:
    data: Optional[List[Dict]] = None
    data_index: int = 1
    is_running: bool = True
    selection: Tuple[int] = field(default_factory=tuple)

    # UI
    ui_manager: pygame_gui.UIManager = None
    ui_window_width: int = 0
    ui_window_height: int = 0
    ui_selection_region: Optional[Tuple[int]] = None
    ui_scroll_x: int = 0
    ui_scroll_y: int = 0
    ui_zoom_factor: int = 20

    @property
    def current_data(self):
        if self.data is None:
            return None
        else:
            return self.data[self.data_index]

    @property
    def dialog_rect(self):
        ww = self.ui_window_width
        wh = self.ui_window_height
        xpad = ww // 10
        ypad = wh // 10
        rect = pygame.Rect(xpad, ypad, ww - 2 * xpad, wh - 2 * ypad)
        return rect

    def stop(self):
        return bind(bind(self).is_running.set(False))

    def set_window_resolution(self, w, h):
        manager = self.ui_manager
        manager.set_window_resolution((w, h))
        self = bind(self)
        self = bind(self.ui_window_width.set(w))
        self = bind(self.ui_window_height.set(h))
        return self
