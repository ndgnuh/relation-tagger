import numpy as np
from dataclasses import dataclass
from typing import List, Callable, Optional


@dataclass(frozen=True, order=True)
class Label:
    text: str


@dataclass(frozen=True, order=True)
class Token:
    text: str
    bbox: List[int]


@dataclass(frozen=True, order=True)
class Menu:
    text: str
    function: Optional[Callable] = None


class Graph:
    def __init__(s, labels, texts, bboxes, adj=None):
        s.labels = [Label(label) for label in labels]
        s.tokens = [Token(text, bbox) for (text, bbox) in zip(texts, bboxes)]
        s.edges = []

        if adj is None:
            return

        ntext = len(texts)
        adj_text = adj[:ntext, :]
        adj_label = adj[ntext:, :]
        for (i, j) in zip(*np.where(adj_text == 1)):
            s.edges.append((s.tokens[i], s.tokens[j]))
        for (i, j) in zip(*np.where(adj_label == 1)):
            s.edges.append((s.labels[i], s.tokens[j]))

    def update_labels(self, labels):
        self.labels = [Label(label) for label in labels]
        self.edges = [(u, v) for (u, v) in self.edges
                      if (u in self.labels or u in self.tokens)
                      and (v in self.labels or v in self.tokens)]

    def toggle_edge(self, i, j):
        nodes = self.nodes
        assert i in nodes
        assert j in nodes
        e = (i, j)
        if e in self.edges:
            self.edges.remove(e)
        else:
            self.edges.append(e)

    def remove_edge(self, i, j):
        if (i, j) in self.edges:
            self.edges.remove((i, j))

    @property
    def nodes(s):
        return s.labels + s.tokens

    @property
    def nlabels(s):
        return len(s.labels)

    @property
    def nedges(s):
        return len(s.edges)

    @property
    def ntokens(s):
        return len(s.tokens)

    @property
    def nnodes(s):
        return len(s.tokens) + len(s.labels)

    @property
    def adj(self):
        nlabels = len(self.labels)
        ntokens = len(self.tokens)
        adj_tokens = np.zeros((ntokens, ntokens), dtype=int)
        adj_labels = np.zeros((nlabels, ntokens), dtype=int)

        for (i, l) in enumerate(self.labels):
            for (j, t) in enumerate(self.tokens):
                if (l, t) in self.edges:
                    adj_labels[i, j] = True

        for (i, u) in enumerate(self.tokens):
            for (j, v) in enumerate(self.tokens):
                if (u, v) in self.edges:
                    adj_tokens[i, j] = True

        return np.concatenate([adj_labels, adj_tokens], axis=0)


if __name__ == "__main__":
    a = Token('asdsa', [1, 2, 1, 1])
    b = Token('what', [2, 2, 1, 1])
    print([b, a])

    print(sorted([a, b]))
