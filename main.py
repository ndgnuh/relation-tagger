from spade_label_tool.state import State
from lenses import bind
from spade_label_tool import static_ui, dynamic_ui
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
    return state.call('set_window_resolution', event.w, event.h)


def handle_event(event, state):
    manager = state.ui_manager.get()

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
        state = state.call('stop')

    handler = event_type_dispatch.get(event.type, None)
    if handler is not None:
        state = handler(event, state)

    manager.process_events(event)
    return state


def main():
    pg.init()
    pg.display.set_caption("Spade label tool")
    root = pg.display.set_mode((800, 600), RESIZABLE)
    ui_manager = pgui.UIManager(root.get_size(), "theme.json")
    state = bind(State(ui_manager=ui_manager))
    state = bind(state.ui_window_width.set(root.get_width()))
    state = bind(state.ui_window_height.set(root.get_height()))

    dui = dynamic_ui.DrawContext(root=root, manager=ui_manager)
    clock = pg.time.Clock()
    static_ui.draw(ui_manager)
    while state.is_running.get():
        time_delta = clock.tick(60) / 1000.0
        for event in pg.event.get():
            state = handle_event(event, state)

        ui_manager.update(time_delta)
        background = pg.Surface(root.get_size())
        background.fill(pg.Color(31, 31, 31))
        root.blit(background, (0, 0))

        ui_manager.draw_ui(root)
        dui.draw(state)
        # pg.draw.line(root, (255, 255, 255), (0, 0), (200, 200), )
        pg.display.update()


if __name__ == "__main__":
    main()
