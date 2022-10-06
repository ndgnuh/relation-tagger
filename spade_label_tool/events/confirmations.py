from spade_label_tool.utils import Functables, write_jsonl_ui

callbacks = Functables()


@callbacks("save_data")
def save_data(event, state):
    elem = event.ui_element
    write_jsonl_ui(state, elem.filepath, elem.data)
    return state


def handle_confirmations(event, state):
    elem = event.ui_element
    action = getattr(elem, 'action')
    if action is None:
        return state

    callback = callbacks.get(action)

    if callback is None:
        return state

    return callback(event, state)
