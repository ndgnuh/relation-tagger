import pygame as pg
import pygame_gui as pgui
from pygame.locals import *
from argparse import Namespace
from functools import cache


def draw_menu(manager: pgui.UIManager,
              button_width: int = 100,
              button_height: int = 33):
    references = dict()
    texts = ["Load", "Save", "Undo", "Redo"]
    current_x = 0
    for text in texts:
        rect = pg.Rect((current_x, 0), (button_width, button_height))
        btn = pgui.elements.UIButton(relative_rect=rect,
                                     text=text,
                                     manager=manager)
        text = text.lower().strip().replace(" ", "_")
        btn.id = f"menu/{text}"
        references[btn.id] = btn
        current_x += button_width
    return references


def draw(manager: pgui.UIManager):
    references = dict()
    references.update(draw_menu(manager))
    return references
