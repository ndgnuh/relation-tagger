import numpy as np
import json
from typing import *
from functools import wraps
from pydantic import BaseModel, Field, PositiveInt


def fallback_dumper(x):
    if isinstance(x, set):
        return list(x)

    raise RuntimeError(f"Cannot deserialize {x} of type {x.__class__.__name__}")


def mutating(f):
    @wraps(f)
    def wrapper(self, *a, **k):
        self.dirty = True
        f(self, *a, **k)

    return wrapper


Point = Tuple[int, int]
Polygon = Tuple[Point, Point, Point, Point]


class Sample(BaseModel):
    texts: List[str]
    boxes: List[Polygon]
    links: Set[Tuple[int, int]] = Field(default_factory=set)

    # classes is modelled as dict because not all node will have classes
    classes: Dict[int, int] = Field(default_factory=dict)

    # unused for now
    image_width: int = 100
    image_height: int = 100
    image_base64: Optional[str] = None

    def image_size(self):
        return (self.image_width, self.image_height)


class Dataset(BaseModel):
    path: str
    classes: List[str]
    samples: List[Sample]
    dirty: bool = False
    idx: PositiveInt = 0

    def __hash__(self):
        return hash((id(self), self.idx, len(self.samples)))

    def __len__(self):
        return len(self.samples)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

    def get_current_sample(self):
        return self.samples[self.idx]

    def get_current_boxes(self):
        sample = self.get_current_sample()
        return boxes

    def get_current_centers(self):
        sample = self.get_current_sample()
        boxes = np.array(sample.boxes)
        centers = boxes.mean(axis=1).round().astype(int)
        return centers.tolist()

    def get_edges(self):
        sample = self.get_current_sample()
        return sample.links

    def next_data(self, delta=1):
        idx = self.idx + delta
        idx = min(idx, len(self.samples) - 1)
        self.idx = idx

    def jump_to(self, idx):
        idx = min(idx, len(self.samples) - 1)
        self.idx = idx

    def previous_data(self, delta=1):
        idx = self.idx - delta
        idx = max(idx, 0)
        self.idx = idx

    def get_text_class(self, node_idx: int):
        sample = self.get_current_sample()
        assert isinstance(node_idx, int) and node_idx < len(sample.texts)
        return sample.classes.get(node_idx, None)

    @mutating
    def set_text_class(self, node_idx: int, class_idx: int):
        sample = self.get_current_sample()
        assert isinstance(node_idx, int) and node_idx < len(sample.texts)
        assert isinstance(class_idx, int)
        if class_idx < 0:
            try:
                sample.classes.pop(node_idx)
            except KeyError:
                pass
        else:
            assert class_idx < len(self.classes)
            sample.classes[node_idx] = class_idx

    @mutating
    def remove_edge(self, i, j):
        sample = self.get_current_sample()
        try:
            sample.links.remove((i, j))
        except KeyError:
            pass

    @mutating
    def add_edge(self, i, j):
        sample = self.get_current_sample()
        sample.links.add((i, j))

    @mutating
    def delete_current_sample(self):
        idx = self.idx
        self.samples.pop(idx)
        self.jump_to(idx)

    def save(self):
        data = self.dict(exclude={"path", "dirty", "idx"})
        data_str = json.dumps(
            data, ensure_ascii=False, indent=4, default=fallback_dumper
        )
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(data_str)
        self.dirty = False


if __name__ == "__main__":
    import json

    with open("data.json") as f:
        data = json.load(f)
    d = Dataset(**data)
    print(d)
