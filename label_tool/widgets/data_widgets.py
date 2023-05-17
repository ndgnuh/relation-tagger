from io import BytesIO
from base64 import b64decode
from argparse import Namespace

import numpy as np
from PIL import Image
from imgui_bundle import imgui, immapp, imgui_md, immvision

from ..states import requires, State
from ..data import Dataset, Sample
from .. import utils
from .node_editor import NodeEditor


@requires(["dataset_file", "dataset"])
def datastatus(state: State):
    dataset = state.dataset
    dataset_file = state.dataset_file

    messages = [
        "Data:",
        "*" if dataset.dirty else "",
        f"[{1 + dataset.idx}/{len(dataset)}] {dataset_file}",
    ]
    for message in messages:
        imgui.same_line()
        imgui.text(message)
    return " ".join(messages)


label_selector_state = Namespace(selected_id=0)


@requires("dataset")
def label_selector(state: State, x=0, y=0):
    static = label_selector_state
    classes = state.dataset.classes
    imgui_md.render_unindented("### Classes")
    imgui.text(" ")

    changed, static.selected_id = imgui.list_box(
        "##label-selector", static.selected_id, classes, len(classes)
    )
    # for (i, class_) in enumerate(classes):
    #     imgui.selectable(class_, False)
    # imgui.end_list_box()


@utils.static
def image_preview_static(static, image_base64, size):
    if static["image"] is None or image_base64 != static["previous_b64"]:
        image = BytesIO(b64decode(image_base64))
        image = Image.open(image)
        image.thumbnail((640, 640)) # Lags
        image = np.array(image)
        static["image"] = image
        static["previous_b64"] = image_base64
    else:
        image = static["image"]

    # Because size is float
    w, h = size
    params = immvision.ImageParams()
    params.image_display_size = (int(w * 1), int(h * 0.8))

    return image, params


@requires("dataset")
def image_preview(state: State):
    if not state.show_image_preview:
        return

    sample: Sample = state.dataset.get_current_sample()
    if sample.image_base64 is not None:
        size = imgui.get_window_size()
        image, params = image_preview_static(sample.image_base64, size)
        immvision.image("## preview", image, params)
    else:
        imgui.text("No image found in this sample, follow the instruction to enable image preview")
        imgui.bullet_text("Load the data")
        imgui.bullet_text("For each sample, read the corresponding image")
        imgui.bullet_text("Save the image to a byte buffer")
        imgui.bullet_text("Convert the byte buffer to base64 encoded string")
        imgui.bullet_text("Store the encoded image string as `image_base64` in the sample")

        imgui.spacing()
        imgui.text("For more information, see `data.py` in the source code for data schema")

@requires("dataset")
def sample_navigator(state):
    data: Dataset = state.dataset

    # Render
    imgui.separator()
    imgui.text_disabled("Sample")
    imgui.separator()

    # Previous
    imgui.bullet()
    if imgui.menu_item("Previous sample", "A", False, True)[0]:
        data.previous_data()

    # Next
    imgui.bullet()
    if imgui.menu_item("Next sample", "D", False, True)[0]:
        data.next_data()

    # Jump
    imgui.bullet()
    imgui.begin_group()
    imgui.text("Jump to sample")
    changed, value = imgui.input_int("##jump-to-sample-idx", data.idx + 1, step=1, step_fast=5)
    if changed:
        data.jump_to(value - 1)
    imgui.end_group()

    # Delete
    imgui.bullet()
    if imgui.menu_item("Delete sample", "", False, True)[0]:
        data.delete_current_sample()


@requires("dataset")
def node_navigator(state):
    data: Dataset = state.dataset
    ned: NodeEditor = state.node_editor

    # Header
    imgui.separator()
    imgui.text_disabled("Node")
    imgui.separator()

    # Check if any node selected
    # Multiple node
    selections = ned.get_node_selections()
    if len(selections) > 1:
        imgui.text("Multiple node selection is not supported")
        return
    elif len(selections) == 0:
        imgui.text("Select a node")
        return

    node_id = selections[0].id
    imgui.bullet()
    imgui.begin_group()
    selection_list = ["(none)"] + data.classes
    selected_idx = data.get_text_class(node_id)
    selected_idx = 0 if selected_idx is None else selected_idx + 1
    imgui.text("Node class:")
    imgui.same_line()
    imgui.text_colored(imgui.ImVec4(0.52, 1, 1, 1), selection_list[selected_idx])
    changed, selected_idx = imgui.list_box("##node-class", selected_idx, selection_list)
    if changed:
        print(changed, selected_idx)
        class_idx = selected_idx - 1
        data.set_text_class(node_id, class_idx)
    imgui.end_group()
    imgui.bullet()
    imgui.menu_item("Split node", "", False, True)


