from imgui_bundle import imgui
from ..states import requires, State


@requires(["dataset_file", "dataset"])
def datastatus(state: State):
    dataset = state.dataset
    dataset_file = state.dataset_file

    messages = [
        "*" if dataset.dirty else "",
        f"[{1 + dataset.idx}/{len(dataset)}] {dataset_file}",
    ]
    for message in messages:
        imgui.same_line()
        imgui.text(message)
