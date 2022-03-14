import pygame.event as pge

signals = [
    # IMPORT LABELS
    "ACTION_IMPORT_LABELS",
    "SUCCESS_IMPORT_LABELS",
    "ERROR_IMPORT_LABELS",
    # LABEL RS
    "ACTION_LABEL_RS",
    "SUCCESS_LABEL_RS",
    # IMPORT DATA
    "ACTION_IMPORT_DATA",
    "SUCCESS_IMPORT_DATA",
    "ERROR_IMPORT_DATA",
    # SELECT IMG DIR
    "ACTION_SELECT_IMGDIR",
    "SUCCESS_SELECT_IMGDIR",
    "ERROR_SELECT_IMGDIR",
    # SAVE SESSION
    "ACTION_SAVE_SESSION",
    "REQUEST_SAVE_SESSION",
    "SUCCESS_SAVE_SESSION",
    "ERROR_SAVE_SESSION",
    # LOAD SESSION
    "ACTION_LOAD_SESSION",
    "REQUEST_LOAD_SESSION",
    "SUCCESS_LOAD_SESSION",
    "ERROR_LOAD_SESSION",
    # BTN PRESS
    "BUTTON_PRESS",
    # DATA NEXT/PREV,
    "ACTION_CHANGE_DATAINDEX",
    "SUCCESS_CHANGE_DATAINDEX",
    # FPS
    "NEW_FRAME",
    # GRAPH
    "ACTION_REL_S",
    "SUCCESS_REL_S",
    "ACTION_REL_G",
    "SUCCESS_REL_G",
    "ACTION_REL_REMOVE",
    "SUCCESS_REL_REMOVE",
    # EXPORT/IMPORT  DATA
    "ACTION_IMPORT_JSON",
    "ACTION_EXPORT_JSON",
    "SUCCESS_EXPORT_JSON",
    # DELETE RECORD
    "ACTION_DELETE_RECORD",
    # COPY TEXT TO CLIPBOARD
    "ACTION_COPY",
    "ACTION_DRAG"
]

for signal in signals:
    exec(f"{signal} = pge.custom_type()")

# Emit or return a function that emit a signal


def emit(sig, **kwargs):
    now = False
    if 'now' in kwargs:
        now = kwargs.pop('now')

    def f():
        e = pge.Event(sig, kwargs)
        pge.post(e)

    if now:
        return f()
    else:
        return f


# JUST A LOOKUP TABLE
class EventHandler:
    def __init__(self):
        self.callbacks = {}

    def register(self, event):
        def f(callback):
            self.callbacks[event] = callback
        return f

    def process_event(self, event, *args, **kwargs):
        callback = self.callbacks.get(event.type)
        if callback:
            callback(event, *args, **kwargs)
