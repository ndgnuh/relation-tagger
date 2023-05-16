from imgui_bundle import imgui, immapp, imgui_md
from ..states import requires, State
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
