from imgui_bundle import imgui, immapp
from dataclasses import dataclass

@dataclass
class Notification:
    title: str
    text: str

@immapp.static(pressed=True)
def notification(title, text):
    static = notification
    if static['pressed']:
        return

    static['trigger']

    imgui.begin(title)
            imgui.begin("Error")
            imgui.text(state.error)
            if imgui.button("OK"):
                state.resolve_error()
            imgui.end()
    imgui.end()


def error_notification()
