from spade_label_tool import (
    state as State,
    dynamic_ui
)
from lenses import bind
from spade_label_tool import static_ui
import pygame_gui as pgui
import pygame as pg
from pygame.locals import *
from spade_label_tool.events import (
    handle_buttons,
    handle_pickers)


def handle_event(event, state):
    # print("Debug", event)
    manager = state.ui.manager.get()
    if event.type == pg.QUIT:
        state = State.stop(state)

    if event.type == pgui.UI_BUTTON_PRESSED:
        state = handle_buttons(event, state)

    if event.type == pg.MOUSEBUTTONUP:
        if event.button == 3:
            state = bind(state.selection.set([]))

    if event.type == pgui.UI_FILE_DIALOG_PATH_PICKED:
        state = handle_pickers(event, state)

    if event.type == pg.VIDEORESIZE:
        state = bind(state.ui.window_width.set(event.w))
        state = bind(state.ui.window_height.set(event.h))
        manager.set_window_resolution((event.w, event.h))
    manager.process_events(event)
    return state


def main():
    state = State.create_state()
    pg.init()
    pg.display.set_caption("Spade label tool")
    root_sf = pg.display.set_mode((800, 600), RESIZABLE)
    state = State.create_ui_manager(state, root_sf)
    state = bind(state.ui.window_width.set(root_sf.get_width()))
    state = bind(state.ui.window_height.set(root_sf.get_height()))
    manager = state.ui.manager.get()

    clock = pg.time.Clock()
    static_ui.draw(manager)
    while state.is_running.get():
        time_delta = clock.tick(60) / 1000.0
        dynamic_ui.draw(state)
        for event in pg.event.get():
            state = handle_event(event, state)

        manager.update(time_delta)
        background = pg.Surface(root_sf.get_size())
        background.fill(pg.Color(31, 31, 31))
        root_sf.blit(background, (0, 0))
        manager.draw_ui(root_sf)
        pg.display.update()


if __name__ == "__main__":
    main()
