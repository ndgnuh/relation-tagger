import numpy as np
from plum import dispatch
from typing import List, Dict


@dispatch
def hash(x: np.ndarray):
    return hash(str(x))


@dispatch
def converge_data(data: List[Dict]):
    # Yes, converge
    # convert the data to a single form
    return [converge_data(d) for d in data]


@dispatch
def converge_data(data: Dict):
    texts = data['texts']
    boxes = np.array(data['bboxes'])
    if boxes.ndim == 3:
        xmin = boxes[..., 0].min(axis=-1)
        ymin = boxes[..., 1].min(axis=-1)
        xmax = boxes[..., 0].max(axis=-1)
        ymax = boxes[..., 1].max(axis=-1)
        boxes = np.stack([xmin, ymin, xmax, ymax], axis=0)

    width = data['width']
    height = data['height']
    boxes_normalized = np.stack([xmin / width, ymin / height,
                                 xmax / width, ymax / height], axis=0)

    return dict(texts=texts,
                boxes=boxes,
                boxes_normalized=boxes_normalized,
                width=width,
                height=height,
                edge_index=[])
