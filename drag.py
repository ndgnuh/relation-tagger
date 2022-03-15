import custom_events as ce
import pygame.key as key
from pygame.locals import MOUSEBUTTONUP, MOUSEBUTTONDOWN, KMOD_SHIFT
from pygame import Rect


# LOCAL STATE
class s:
    start_x = 0
    start_y = 0
    end_x = 0
    end_y = 0
    dragging = False


def process_event(event):
    if event.type == MOUSEBUTTONDOWN and event.button == 1:
        s.dragging = True
        s.start_x, s.start_y = event.pos

    if event.type == MOUSEBUTTONUP and s.dragging:
        s.dragging = False
        s.end_x, s.end_y = event.pos
        region = Rect(s.start_x,
                      s.start_y,
                      s.end_x - s.start_x,
                      s.end_y - s.start_y)
        if region.width > 20 and region.height > 20:
            ce.emit(ce.ACTION_DRAG, region=region, now=True)
