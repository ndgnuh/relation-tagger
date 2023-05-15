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
    in_pin_id: ed.PinId = field(default_factory=ed.PinId.create)
    out_pin_id: ed.PinId = field(default_factory=ed.PinId.create)

    def __hash__(self):
        return hash((self.text, self.x, self.y))

    def __init__(self, text, x, y, node_id: int):
        self.text = text
        self.x = x
        self.y = y
        self.node_id = ed.NodeId.create()
        self.in_pin_id = ed.PinId.create()
        self.out_pin_id = ed.PinId.create()

    # def __post_init__(self):
    #     ed.set_node_position(self.node_id, imgui.ImVec2(self.x, self.y))

    def draw(self):
        ed.begin_node(self.node_id)
        ed.begin_pin(self.in_pin_id, ed.PinKind.input)
        imgui.text(">")
        ed.end_pin()

        imgui.same_line()
        imgui.text(self.text)

        imgui.same_line()
        ed.begin_pin(self.out_pin_id, ed.PinKind.output)
        imgui.text(">")
        ed.end_pin()

        ed.end_node()


@dataclass
class Link:
    link_id: ed.LinkId
    from_id: ed.PinId
    to_id: ed.PinId

    def draw(self):
        ed.link(self.link_id, self.from_id, self.to_id)


@dataclass
class NodeEditor:
    def __init__(self, texts, boxes, links):
        self.texts = [(text, x, y) for (text, (x, y)) in zip(texts, boxes)]
        self.edge_index = links
        self.nodes = []
        for (i, text) in enumerate(texts):
            node = Node(text, *boxes[i], node_id=i)
            self.nodes.append(node)
        self.init_links()

    def init_links(self):
        self.links = []
        for k, (i, j) in enumerate(self.edge_index):
            link_id = ed.LinkId(k)
            from_id = self.nodes[i].out_pin_id
            to_id = self.nodes[j].in_pin_id
            link = Link(link_id, from_id, to_id)
            self.links.append(link)
        self.register = print

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
