import math
from imgui_bundle import imgui, imgui_node_editor as ed, ImVec4
from dataclasses import dataclass, field
from typing import List, Set, Tuple, Dict


@dataclass
class IdProvider:
    idx: int = 1

    def next(self):
        self.idx += 1
        return self.idx

    def reset(self):
        self.idx = 1


@dataclass
class Node:
    text: str
    x: int
    y: int
    node_id: ed.NodeId = field(default_factory=ed.NodeId.create)
    in_pin: ed.PinId = field(default_factory=ed.PinId.create)
    out_pin: ed.PinId = field(default_factory=ed.PinId.create)

    def __hash__(self):
        return hash((self.text, self.x, self.y))

    def draw(self):
        pin_text = "."
        ed.begin_node(self.node_id)

        ed.begin_pin(self.in_pin, ed.PinKind.input)
        imgui.text(pin_text)
        ed.end_pin()

        imgui.same_line()
        imgui.text(self.text)

        imgui.same_line()
        ed.begin_pin(self.out_pin, ed.PinKind.output)
        imgui.text(pin_text)
        ed.end_pin()

        ed.end_node()


@dataclass
class Link:
    link_id: ed.LinkId
    from_node: Node
    to_node: Node

    def draw(self):
        from_pin = self.from_node.out_pin
        to_pin = self.to_node.in_pin
        ed.link(ed.LinkId(self.link_id), from_pin, to_pin)


class NodeEditor:
    def __init__(self, texts, boxes, links, dataset):
        self.texts = [(text, x, y) for (text, (x, y)) in zip(texts, boxes)]
        self.edge_index = links
        self.nodes = []
        self.links = []
        for i, text in enumerate(texts):
            node = Node(text, *boxes[i])
            self.nodes.append(node)
        self.init_links()

    def init_links(self):
        self.links = []
        for k, (i, j) in enumerate(self.edge_index):
            link = Link(k, self.nodes[i], self.nodes[j])
            self.links.append(link)

    def on_frame(self):
        ed.begin("Node editor", imgui.ImVec2(0, 0))

        for node in self.nodes:
            node.draw()

        for link in self.links:
            link.draw()

        if imgui.is_key_pressed(imgui.Key.s):
            self.create_edges_from_selections()
        ed.end()

    def create_edges_from_selections(self):
        sel = self.get_node_selections()
        n = len(sel)
        for in_node, out_node in zip(sel, sel[1:]):
            i = self.nodes.index(in_node)
            j = self.nodes.index(out_node)
            self.edge_index.add((i, j))
        self.init_links()

    def get_node_selections(self):
        sel = []
        for node in self.nodes:
            if ed.is_node_selected(node.node_id):
                sel.append(node)

        def key(node):
            pos = ed.get_node_position(node_id=node.node_id)
            return pos[0] + pos[1]

        if len(sel) < 2:
            return []
        sel = sorted(sel, key=key)
        print([node.text for node in sel])
        return sel
