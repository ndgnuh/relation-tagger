from typing import *
from dataclasses import dataclass, _MISSING_TYPE, field


@dataclass
class Configuration:
    @classmethod
    def from_dict(cls, d):
        fields = cls.__dataclass_fields__
        options = dict()
        for k in d:
            if k not in fields:
                raise ValueError(f"Unexpected key {k} for type {cls}")
        for k, v in fields.items():
            if k not in d and v.default == _MISSING_TYPE:
                raise ValueError(f"Expected key {k} for type {cls}")
            if k in d:
                options[k] = d[k]

        return cls(**options)

    def __hash__(self):
        return hash(tuple(tuple(v) for v in vars.self.items()))


@dataclass(eq=True)
class Sample(Configuration):
    texts: List[str]
    boxes: List[Tuple[int, int]]
    links: List[Tuple[int, int]] = field(default_factory=list)

    def __hash__(self):
        return id(self)


@dataclass(eq=True)
class Dataset(Configuration):
    classes: List[str]
    samples: List[Sample]
    idx: int = 0

    def __post_init__(self):
        self.samples = [Sample.from_dict(s) for s in self.samples]

    def __hash__(self):
        return hash((id(self), self.idx))

    def get_current_sample(self):
        return self.samples[self.idx]


if __name__ == "__main__":
    import json
    with open("data.json") as f:
        data = json.load(f)
    d = Dataset.from_dict(data)
    print(d)
