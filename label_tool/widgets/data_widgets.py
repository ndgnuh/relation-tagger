from base64 import b64decode
from io import BytesIO

import numpy as np
from PIL import Image
from imgui_bundle import imgui, immapp, imgui_md, immvision

from ..states import requires, State
from ..data import Dataset, Sample
from argparse import Namespace


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

def static(f):
    from functools import wraps
    from argparse import Namespace
    from collections import defaultdict
    static = defaultdict(lambda *a, **k: None)

    @wraps(f)
    def wrapped(*a, **k):
        return f(static, *a, **k)
    return wrapped

@static
def image_preview_static(static, image_base64, size):
    if static['image'] is None or image_base64 != static['previous_b64']:
        image = BytesIO(b64decode(image_base64))
        image = Image.open(image)
        image = np.array(image)
        static['image'] = image
        static['previous_b64'] = image_base64
    else:
        image = static['image']

    # Because size is float
    w, h = size
    params = immvision.ImageParams()
    params.image_display_size = (int(w * 0.7), int(h * 0.7))

    return image, params

@requires("dataset")
def image_preview(state: State):
    if not state.show_image_preview:
        return

    imgui.begin("Preview")
    sample: Sample = state.dataset.get_current_sample()
    size = imgui.get_window_size()
    image, params = image_preview_static(sample.image_base64, size)
    immvision.image("## preview", image, params)
    imgui.end()
