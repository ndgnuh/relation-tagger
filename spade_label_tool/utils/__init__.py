from spade_label_tool.utils.functables import *
from spade_label_tool.utils.cache import memoize, custom_hash
from pygame_gui.windows import UIMessageWindow
import json
import pygame


def safe_call(func):
    def wrapper(*args, **kwds):
        try:
            result = func(*args, **kwds)
            return result, None
        except Exception as e:
            return None, e
    return wrapper


@safe_call
def read_jsonl(path: str):
    with open(path, encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines()]
        lines = [line for line in lines if len(line) > 0]
    data = [json.loads(line) for line in lines]
    return data


@safe_call
def write_jsonl(path: str, data):
    def serialize(d):
        out = dict()
        out['texts'] = d['texts']
        out['boxes'] = d['boxes'].tolist()
        out['edge_index'] = list(d['edge_index'])
        out['width'] = d['width']
        out['height'] = d['height']
        return out
    wdata = list(map(serialize, data))
    data_str = json.dumps(wdata)
    with open(path, "w", encoding="utf-8") as f:
        f.write(data_str)


def write_jsonl_ui(state, path, data):
    manager = state.ui_manager.get()
    rect = state.dialog_rect.get()
    data, error = write_jsonl(path, data)
    if error:
        UIMessageWindow(html_message=f"Error {error}",
                        manager=manager,
                        rect=rect)
    else:
        UIMessageWindow(html_message=f"Success, data to {path}",
                        manager=manager,
                        rect=rect)


def get_rect(x1, y1, x2, y2):
    return pygame.Rect(x1, y1, x2 - x1, y2-y1)
