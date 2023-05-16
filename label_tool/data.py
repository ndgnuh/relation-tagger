from typing import *
from dataclasses import dataclass, _MISSING_TYPE, field
from pydantic import BaseModel, Field



class Sample(BaseModel):
    texts: List[str]
    boxes: List[Tuple[int, int]]
    links: List[Tuple[int, int]] = Field(default_factory=list)



class Dataset(BaseModel):
    classes: List[str]
    samples: List[Sample]
    idx: int = 0

    def __hash__(self):
        return hash((id(self), self.idx))

    def get_current_sample(self):
        return self.samples[self.idx]


if __name__ == "__main__":
    import json
    with open("data.json") as f:
        data = json.load(f)
    d = Dataset(**data)
    print(d)
