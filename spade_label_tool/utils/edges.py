# This module serve only one purpose: find connection point :(
# Cases:
# - same row
# - same column
# - same row AND column
# - none of the above

from plum import dispatch
from pygame import Rect
from typing import Dict, Any, Tuple

vpos = ["t", "b"]
hpos = ["l", "r"]


def find_relationship(box1, box2):
    samerow = box1.top >= box2.bottom and box2.top >= box1.bottom
    samecol = box1.left >= box2.right and box2.left >= box1.right


@dispatch
def find_endpoints(box1: Rect, box2: Rect):
    samerow = (box1.top < box2.bottom) and (box1.bottom > box2.top)
    samecol = (box1.left < box2.right) and (box1.right > box2.left)
    if samerow and not samecol:
        print("Same row")
        if box1.right <= box2.left:
            return box1.midright, box2.midleft
        elif box2.right <= box1.left:
            return box2.midright, box1.midleft
        else:
            print("SR fallback")
    elif samecol and not samerow:
        print("Same col")
        if box1.bottom <= box2.top:
            return box1.midbottom, box2.midtop
        elif box2.bottom <= box1.top:
            return box2.midbottom, box1.midtop
        else:
            print("SC fallback")
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
