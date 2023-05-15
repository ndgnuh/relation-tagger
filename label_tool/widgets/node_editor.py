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
    t_pin: ed.PinId = field(default_factory=ed.PinId.create)
    b_pin: ed.PinId = field(default_factory=ed.PinId.create)
    l_pin: ed.PinId = field(default_factory=ed.PinId.create)
    r_pin: ed.PinId = field(default_factory=ed.PinId.create)
    tr_pin: ed.PinId = field(default_factory=ed.PinId.create)
    tl_pin: ed.PinId = field(default_factory=ed.PinId.create)
    br_pin: ed.PinId = field(default_factory=ed.PinId.create)
    bl_pin: ed.PinId = field(default_factory=ed.PinId.create)

    def __hash__(self):
        return hash((self.text, self.x, self.y))

    def draw_group(self, pins, texts):
        imgui.begin_group()
        longest = max(map(len, texts))
        for (pin, text) in zip(pins, texts):
            text = text * (longest // len(text))
            if pin is not None:
                ed.begin_pin(pin, ed.PinKind.output)
                imgui.text(text)
                ed.end_pin()
            else:
                imgui.text(text)
        imgui.end_group()

    def draw(self):
        pin_text = "*"
        ed.begin_node(self.node_id)

        self.draw_group(
            [self.tl_pin, self.l_pin, self.bl_pin],
            [pin_text] * 3
        )

        imgui.same_line()
        self.draw_group(
            [self.t_pin, None, self.b_pin],
            [pin_text, self.text, pin_text]
        )

        imgui.same_line()
        self.draw_group(
            [self.tr_pin, self.r_pin, self.br_pin],
            [pin_text] * 3
        )

        ed.end_node()


@dataclass
class Link:
    link_id: ed.LinkId
    from_node: Node
    to_node: Node

    def draw(self):
        w1, h1 = ed.get_node_size(self.from_node.node_id)
        w2, h2 = ed.get_node_size(self.to_node.node_id)
        x1, y1 = ed.get_node_position(self.from_node.node_id)
        x2, y2 = ed.get_node_position(self.to_node.node_id)
        x1 = x1 + w1//2
        x2 = x2 + w2//2
        y1 = y1 + h1//2
        y2 = y2 + h2//2
        angle = math.atan2(y2 - y1, x2 - x1)
        angle = (angle + math.pi) / math.pi / 2
        angle = int(angle * 8 * 8 - 0.5) // 8
        mapping = [
            ("tl", "br"),
            ("t", "b"),
            ("tr", "bl"),
            ("r", "l"),
            ("br", "tl"),
            ("b", "t"),
            ("bl", "tr"),
            ("l", "r"),
        ]
        try:
            s, e = mapping[angle]
        except Exception:
            print("__")
            print(y1, y2, x1, x2)
            angle = math.atan2(y1 - y2, x1 - x2)
            print('a1', angle)
            angle = (angle + math.pi) / math.pi / 2
            print('a2', angle)
            angle = int(angle * 8 * 8) // 8
            print('a3', angle)
            return
        s = f"{s}_pin"
        e = f"{e}_pin"
        from_pin = getattr(self.from_node, s)
        to_pin = getattr(self.to_node, e)
        ed.link(ed.LinkId(self.link_id), from_pin, to_pin)


class NodeEditor:
    def __init__(self, texts, boxes, links):
        self.texts = [(text, x, y) for (text, (x, y)) in zip(texts, boxes)]
        self.edge_index = set([(i, j) for (i, j) in links])
        self.nodes = []
        self.links = []
        for (i, text) in enumerate(texts):
            node = Node(text, *boxes[i])
            self.nodes.append(node)
        self.init_links()

    def init_links(self):
        self.links = []
        for (k, (i, j)) in enumerate(self.edge_index):
            link = Link(k, self.nodes[i], self.nodes[j])
            self.links.append(link)

    def on_frame(self):
        ed.begin("Node editor", imgui.ImVec2(0, 0))

        for node in self.nodes:
            node.draw()

        for link in self.links:
            link.draw()

        ed.end()

    def _get_node_selections(self):
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
