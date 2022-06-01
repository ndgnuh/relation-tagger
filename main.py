from spade_label_tool import state as State
from spade_label_tool import static_ui
import pygame_gui as pgui
import pygame as pg
from pygame.locals import *


def main():
    state = State.create_state()
    pg.init()
    pg.display.set_caption("Spade label tool")
    root_sf = pg.display.set_mode((800, 600), RESIZABLE)
    manager = pgui.UIManager(root_sf.get_size())
    ui = static_ui.draw(manager)

    clock = pg.time.Clock()
    while state.is_running.get():
        time_delta = clock.tick(60) / 1000.0
        for event in pg.event.get():
            if event.type == pg.QUIT:
                state = State.stop(state)

            manager.process_events(event)

        manager.update(time_delta)
        background = pg.Surface(root_sf.get_size())
        background.fill(pg.Color(31, 31, 31))
        root_sf.blit(background, (0, 0))
        manager.draw_ui(root_sf)
        pg.display.update()


if __name__ == "__main__":
    main()
