# This module serve only one purpose: find connection point :(
# Cases:
# - same row
# - same column
# - same row AND column
# - none of the above

from plum import dispatch
from pygame import Rect
from typing import Dict, Any, Tuple


class LeftTo:
    def __init__(self, box1, box2):
        box1, box2 = (box1, box2) if box1.right < box2.left else (box2, box1)
        self.box1 = box1
        self.box2 = box2


class TopTo:
    def __init__(self, box1, box2):
        box1, box2 = (box1, box2) if box1.bottom < box2.top else (box2, box1)
        self.box1 = box1
        self.box2 = box2


class LeftTopTo:
    def __init__(self, box1, box2):
        box1, box2 = (box1, box2) \
            if (box1.bottom < box2.top) and (box1.right < box2.left)\
            else (box2, box1)
        self.box1 = box1
        self.box2 = box2


relation_mapping: Dict[Tuple, Any] = dict()
relation_mapping[(False, False)] = LeftTopTo
relation_mapping[(False, True)] = LeftTo
relation_mapping[(True, False)] = TopTo
# TODO
# Overlap box


def find_relationship(box1, box2):
    samerow = box1.top >= box2.bottom and box2.top >= box1.bottom
    samecol = box1.left >= box2.right and box2.left >= box1.right
    return relation_mapping[(samerow, samecol)](box1, box2)


@dispatch
def find_endpoints(box1: Rect, box2: Rect):
    relation = find_relationship(box1, box2)
    print(box1, box2, relation)
    return box1.center, box2.center
    # return find_endpoints(box1, box2, relation)
