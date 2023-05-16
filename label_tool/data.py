import numpy as np
import json
from typing import *
from functools import wraps
from pydantic import BaseModel, Field


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


class Dataset(BaseModel):
    path: str
    classes: List[str]
    samples: List[Sample]
    dirty: bool = False
    idx: int = 0

    def __hash__(self):
        return hash((id(self), self.idx))

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

    def get_current_sample(self):
        return self.samples[self.idx]

    def get_current_centers(self):
        sample = self.get_current_sample()
        boxes = np.array(sample.boxes)
        centers = boxes.mean(axis=1).round().astype(int)
        return centers.tolist()

    def get_edges(self):
        sample = self.get_current_sample()
        return sample.links

    @mutating
    def add_edge(self, i, j):
        sample = self.get_current_sample()
        sample.links.add((i, j))

    def save(self):
        data = self.dict(exclude={"path", "dirty", "idx"})
        data_str = json.dumps(data, ensure_ascii=False, indent=4, default=fallback_dumper)
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(data_str)
        self.dirty = False


if __name__ == "__main__":
    import json

    with open("data.json") as f:
        data = json.load(f)
    d = Dataset(**data)
    print(d)
