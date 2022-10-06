from spade_label_tool.utils.functables import *
from spade_label_tool.utils.cache import memoize, custom_hash
import json
import pygame


def read_jsonl(path: str):
    try:
        with open(path, encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines()]
            lines = [line for line in lines if len(line) > 0]
        data = [json.loads(line) for line in lines]
        error = None
    except Exception as e:
        data = None
        error = e
    return data, error


def get_rect(x1, y1, x2, y2):
    return pygame.Rect(x1, y1, x2 - x1, y2-y1)
