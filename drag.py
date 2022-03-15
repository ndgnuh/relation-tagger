import custom_events as ce
from pygame.locals import MOUSEBUTTONUP, MOUSEBUTTONDOWN, MOUSEMOTION
from pygame import Rect


# LOCAL STATE
class s:
    start_x = 0
    start_y = 0
    end_x = 0
    end_y = 0
    dragging = False
    # Set to true when mouse click
    maybe_dragging = False

    @classmethod
    def xy(cls):
        x1 = min(s.start_x, s.end_x)
        x2 = max(s.start_x, s.end_x)
        y1 = min(s.start_y, s.end_y)
        y2 = max(s.start_y, s.end_y)
        return x1, x2, y1, y2

    @classmethod
    def rect(cls):
        x1, x2, y1, y2 = cls.xy()
        return Rect(x1, y1, x2 - x1, y2 - y1)


def process_event(event):
    if not s.dragging:
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            s.maybe_dragging = True
            s.start_x, s.start_y = event.pos

    if event.type == MOUSEMOTION and s.maybe_dragging:
        s.end_x, s.end_y = event.pos
        if abs(s.start_x - s.end_x) > 10 \
                and abs(s.start_y - s.end_y) > 10:
            s.dragging = True
            ce.emit(ce.ACTION_DRAG_RESIZE, region=s.rect(), now=True)

    if event.type == MOUSEBUTTONUP:
        s.maybe_dragging = False
        if s.dragging:
            s.dragging = False
            s.end_x, s.end_y = event.pos
            region = s.rect()
            if region.width > 20 and region.height > 20:
                s.end_x = s.start_x = 0
                s.end_y = s.start_y = 0
                ce.emit(ce.ACTION_DRAG, region=region, now=True)


def is_dragging():
    return s.dragging


def drag_region():
    return s.rect()
