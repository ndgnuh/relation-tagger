import pygame as pg
import pygame_gui as pgui
from pygame.locals import *
from argparse import Namespace


def draw(manager):
    ns = Namespace()
    x = 0
    ns.import_label_btn = pgui.elements.UIButton(
        relative_rect=pg.Rect((0, 0), (-1, 50)),
        text='Import label',
        manager=manager)
    x += ns.import_label_btn.relative_rect.width
    ns.import_btn = pgui.elements.UIButton(
        relative_rect=pg.Rect((x, 0), (100, 50)),
        text='Import',
        manager=manager)
    x += ns.import_btn.relative_rect.width
    ns.export_btn = pgui.elements.UIButton(
        relative_rect=pg.Rect((x, 0), (100, 50)),
        text='Export',
        manager=manager)
    # x += ns.export_btn.relative_rect.width
    # ns.import_data = pgui.elements.UIButton(
    #     relative_rect=pg.Rect((x, 0), (100, 50)),
    #     text='Import data',
    #     manager=manager)
    return ns
