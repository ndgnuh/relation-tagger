import math
import unicodedata
from itertools import product
from dataclasses import dataclass, field
from typing import List, Set, Tuple, Dict, Optional

import numpy as np
from imgui_bundle import imgui, imgui_node_editor as ed, ImVec4
from ..states import State
from .. import utils


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
    id: str
    text: str
    x: int
    y: int
    node_id: ed.NodeId = field(default_factory=ed.NodeId.create)
    in_pin: ed.PinId = field(default_factory=ed.PinId.create)
    out_pin: ed.PinId = field(default_factory=ed.PinId.create)

    def __post_init__(self):
        ed.set_node_position(self.node_id, imgui.ImVec2(self.x, self.y))

    def __hash__(self):
        return hash((self.text, self.x, self.y))

    def draw(self, class_name: Optional[str] = None, num_initials: int = 1):
        pin_text = " "
        ed.begin_node(self.node_id)
        h = imgui.get_text_line_height()

        ed.begin_pin(self.in_pin, ed.PinKind.input)
        imgui.dummy(imgui.ImVec2(1, h))
        ed.end_pin()

        imgui.same_line()
        imgui.begin_group()
        if class_name is not None:
            if num_initials == 0:
                class_name_str = class_name.title()
            else:
                class_name_str = class_name[0:num_initials].title()
            imgui.text_colored(imgui.ImVec4(0.52, 1, 1, 1), class_name_str)

        imgui.same_line()
        imgui.text(self.text)
        imgui.end_group()

        imgui.same_line()
        ed.begin_pin(self.out_pin, ed.PinKind.output)
        imgui.dummy(imgui.ImVec2(1, h))
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


def rescale_boxes(boxes, scale=1920):
    boxes = np.array(boxes)
    boxes = 1.0 * boxes * scale / boxes.max()
    boxes = boxes.round().astype(int)
    return boxes.tolist()


class NodeEditor:
    def __init__(self, dataset):
        sample = dataset.get_current_sample()
        self.texts = sample.texts
        self.boxes = sample.boxes
        self.dataset = dataset
        self.nodes = []
        self.centers = np.array(rescale_boxes(self.boxes)).mean(axis=1)
        count = 0
        for text, center in zip(self.texts, self.centers):
            self.nodes.append(Node(count, text, *center))
            count += 1
        self.init_links()

    def init_links(self):
        links = []
        edge_index = self.dataset.get_edges()
        for k, (i, j) in enumerate(edge_index):
            link = Link(k, self.nodes[i], self.nodes[j])
            links.append(link)
        self.links = links

    def on_frame(self):
        ed.begin("Node editor", imgui.ImVec2(0, 0))

        for node in self.nodes:
            class_id = self.dataset.get_text_class(node.id)
            if class_id is None:
                node.draw()
            else:
                node.draw(self.dataset.classes[class_id])

        for link in self.links:
            link.draw()

        if imgui.is_key_pressed(imgui.Key.s):
            self.create_edges_from_selections()
        if imgui.is_key_pressed(imgui.Key.r):
            self.delete_edges_from_selections()
        ed.end()

    def delete_edges_from_selections(self):
        sel = self.get_node_selections()
        from itertools import product

        for in_node, out_node in product(sel, sel):
            i = self.nodes.index(in_node)
            j = self.nodes.index(out_node)
            self.dataset.remove_edge(i, j)
        self.init_links()
        self.deselect_all()

    def create_edges_from_selections(self):
        sel = self.get_node_selections()
        for in_node, out_node in zip(sel, sel[1:]):
            i = self.nodes.index(in_node)
            j = self.nodes.index(out_node)
            self.dataset.add_edge(i, j)
        self.init_links()
        self.deselect_all()

    def deselect_all(self):
        for node in self.get_node_selections():
            ed.deselect_node(node.node_id)

    def get_node_selections(self):
        sel = []
        for node in self.nodes:
            if ed.is_node_selected(node.node_id):
                sel.append(node)

        def key(node):
            pos = ed.get_node_position(node_id=node.node_id)
            return pos[1] + pos[0]

        sel = sorted(sel, key=key)
        return sel


# Re-Re-write


def get_cache_key(state: State):
    if state.dataset is None:
        return -1
    key = (state.dataset_file, state.dataset.idx, len(state.dataset.samples))

    return hash(key)


def node_editor_init_links(state):
    data = state.dataset
    sample = data.get_current_sample()
    nodes = state.node_editor_nodes
    links = []
    for k, (i, j) in enumerate(sample.links):
        link = Link(k, nodes[i], nodes[j])
        links.append(link)
    state.node_editor_links = links


def node_editor_init(state):
    # import logging
    # logging.getLogger().setLevel(logging.DEBUG)
    # logging.debug("init")
    data = state.dataset
    sample = data.get_current_sample()
    texts = sample.texts
    boxes = sample.boxes
    nodes = []
    centers = np.array(rescale_boxes(boxes)).mean(axis=1)

    # Init nodes
    for count, (text, center) in enumerate(zip(texts, centers)):
        nodes.append(Node(count, text, *center))

    # Init links
    links = []
    for k, (i, j) in enumerate(sample.links):
        link = Link(k, nodes[i], nodes[j])
        links.append(link)

    state.node_editor_nodes = nodes
    state.node_editor_links = links


def node_editor_get_selected_nodes(state: State) -> List[Node]:
    sel = []
    for node in state.node_editor_nodes:
        if ed.is_node_selected(node.node_id):
            sel.append(node)

    def key(node):
        pos = ed.get_node_position(node_id=node.node_id)
        return pos[1] + pos[0]

    sel = sorted(sel, key=key)
    return sel


def node_editor_deselect(state):
    for node in node_editor_get_selected_nodes(state):
        ed.deselect_node(node.node_id)


def node_editor_add_links(state: State):
    selections = node_editor_get_selected_nodes(state)
    nodes = state.node_editor_nodes
    for in_node, out_node in zip(selections, selections[1:]):
        i = nodes.index(in_node)
        j = nodes.index(out_node)
        state.dataset.add_edge(i, j)
    node_editor_init_links(state)
    node_editor_deselect(state)
    state.node_editor_add_links = False


def node_editor_remove_links(state: State):
    selections = node_editor_get_selected_nodes(state)
    nodes = state.node_editor_nodes
    for in_node, out_node in product(selections, selections):
        i = nodes.index(in_node)
        j = nodes.index(out_node)
        state.dataset.remove_edge(i, j)
    node_editor_init_links(state)
    node_editor_deselect(state)
    state.node_editor_remove_links = False


previous_cache_key = None


def node_editor(state: State):
    if state.dataset is None:
        return
    global previous_cache_key
    this_cache_key = get_cache_key(state)
    if this_cache_key != previous_cache_key or state.node_editor_reinit:
        node_editor_init(state)
        state.node_editor_reinit = False
    previous_cache_key = this_cache_key

    #
    # Draw nodes and edges
    #
    ed.begin("Editor")
    # Draw nodes
    class_names = state.dataset.classes
    for node in state.node_editor_nodes:
        class_idx = state.dataset.get_text_class(node.id)
        if class_idx is None:
            node.draw()
        else:
            node.draw(
                class_names[class_idx],
                num_initials=state.node_editor_num_class_initials,
            )
    # Draw links
    for link in state.node_editor_links:
        link.draw()
    ed.end()

    #
    # Handle signals
    #
    if state.node_editor_add_links:
        node_editor_add_links(state)
    if state.node_editor_remove_links:
        node_editor_remove_links(state)

    # Update state
    state.node_editor_selections = node_editor_get_selected_nodes(state)
