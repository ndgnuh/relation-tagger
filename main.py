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
    handle_pickers,
    handle_mouse,
    handle_keyboard,
    handle_confirmations
)


def handle_resize(event, state):
    manager = state.ui.manager.get()
    manager.set_window_resolution((event.w, event.h))
    state = bind(state.ui.window_width.set(event.w))
    state = bind(state.ui.window_height.set(event.h))
    return state


def handle_event(event, state):
    manager = state.ui.manager.get()

    event_type_dispatch = {
        pg.VIDEORESIZE: handle_resize,
        pg.MOUSEBUTTONUP: handle_mouse,
        pg.MOUSEBUTTONDOWN: handle_mouse,
        pg.MOUSEMOTION: handle_mouse,
        pg.MOUSEWHEEL: handle_mouse,
        # pg.KEYDOWN: handle_keyboard,
        pg.KEYUP: handle_keyboard,
        pgui.UI_CONFIRMATION_DIALOG_CONFIRMED: handle_confirmations,
        pgui.UI_BUTTON_PRESSED: handle_buttons,
        pgui.UI_FILE_DIALOG_PATH_PICKED: handle_pickers,
    }
    # if event.type not in event_type_dispatch:
    #     print('unk', event)

    if event.type == pg.QUIT:
        state = State.stop(state)

    handler = event_type_dispatch.get(event.type, None)
    if handler is not None:
        state = handler(event, state)

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

    dui = dynamic_ui.DrawContext(root=root_sf, manager=manager)
    clock = pg.time.Clock()
    static_ui.draw(manager)
    while state.is_running.get():
        time_delta = clock.tick(60) / 1000.0
        for event in pg.event.get():
            state = handle_event(event, state)

        manager.update(time_delta)
        background = pg.Surface(root_sf.get_size())
        background.fill(pg.Color(31, 31, 31))
        root_sf.blit(background, (0, 0))
        # print('container', vars(state.ui.manager.get().root_container))

        manager.draw_ui(root_sf)
        dui.draw(state)
        # pg.draw.line(root_sf, (255, 255, 255), (0, 0), (200, 200), )
        pg.display.update()


if __name__ == "__main__":
    main()
