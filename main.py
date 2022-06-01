import spade_label_tool.state as State
import pandas as pd
from lenses import bind
import pygame_gui as pgui
import pygame as pg
from pygame.locals import *


def main():
    state = State.create_state()
    pg.init()
    pg.display.set_caption("Spade label tool")
    root_sf = pg.display.set_mode((800, 600), RESIZABLE)
    manager = pgui.UIManager(root_sf.get_size())
    while state.is_running.get():
        for event in pg.event.get():
            if event.type == pg.QUIT:
                state = State.stop(state)

        background = pg.Surface(root_sf.get_size())
        background.fill(pg.Color(90, 90, 90))
        root_sf.blit(background, (0, 0))
        pg.display.update()


if __name__ == "__main__":
    main()
