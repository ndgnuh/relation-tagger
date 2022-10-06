# This module serve only one purpose: find connection point :(
# Cases:
# - same row
# - same column
# - same row AND column
# - none of the above

from plum import dispatch
from pygame import Rect


@dispatch
def find_endpoints(box1: Rect, box2: Rect):
    samerow = (box1.top < box2.bottom) and (box1.bottom > box2.top)
    samecol = (box1.left < box2.right) and (box1.right > box2.left)
    if samerow and not samecol:
        if box1.right <= box2.left:
            return box1.midright, box2.midleft
        elif box2.right <= box1.left:
            return box2.midright, box1.midleft
    elif samecol and not samerow:
        if box1.bottom <= box2.top:
            return box1.midbottom, box2.midtop
        elif box2.bottom <= box1.top:
            return box2.midbottom, box1.midtop
    else:
        if box1.bottom < box2.bottom:
            y0, y1 = box1.bottom, box2.top
        else:
            y0, y1 = box1.top, box2.bottom

        if box1.left < box2.left:
            x0, x1 = box1.right, box2.left
        else:
            x0, x1 = box1.left, box2.right
        return (x0, y0), (x1, y1)
    return box1.center, box2.center
