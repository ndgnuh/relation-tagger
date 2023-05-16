import numpy as np
from typing import *
from dataclasses import dataclass, _MISSING_TYPE, field
from pydantic import BaseModel, Field


Point = Tuple[int, int]
Polygon = Tuple[Point, Point, Point, Point]

class Sample(BaseModel):
    texts: List[str]
    boxes: List[Polygon]
    links: Set[Tuple[int, int]] = Field(default_factory=set)



class Dataset(BaseModel):
    classes: List[str]
    samples: List[Sample]
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

if __name__ == "__main__":
    import json
    with open("data.json") as f:
        data = json.load(f)
    d = Dataset(**data)
    print(d)
