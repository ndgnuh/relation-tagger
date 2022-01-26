import custom_events as ce
import tkinter as tk
import tkinter.filedialog as filedialog
import pandas as pd
from ast import literal_eval
import traceback
import pickle
import json
import cv2
import os

REL_S_KEY = 'graph_s'
REL_G_KEY = 'graph_g'
eh = ce.EventHandler()


def tk_dialog(dl):
    root = tk.Tk()
    root.withdraw()
    return dl()


def pick_file():
    file = tk_dialog(filedialog.askopenfile)
    if file is None:
        return file
    file.close()
    name = file.name
    return name


def pick_save_file():
    file = tk_dialog(filedialog.asksaveasfile)
    if file is not None:
        name = file.name
        file.close()
        return name


def pick_directory():
    d = tk_dialog(filedialog.askdirectory)
    return d


def data_to_json(row, state, field_rs):
    def bbox_to_coord(b):
        x1, x2, y1, y2 = b
        return [[x1, y1],
                [x2, y1],
                [x2, y2],
                [x1, y2]]
    j = {}
    j['data_id'] = row['img_id']
    j['fields'] = state.labels
    j['field_rs'] = field_rs
    j['text'] = list(row['img_texts'])
    j['label'] = [
        row[REL_S_KEY].adj.tolist(),
        row[REL_G_KEY].adj.tolist()]
    print('n rel_g: ', len(row[REL_G_KEY].edges))
    j['coord'] = [bbox_to_coord(b) for b in row['img_bboxes']]
    j['vertical'] = [False for _ in (row['img_texts'])]
    if state.imgdir is not None:
        height, width, _ = cv2.imread(
            os.path.join(state.imgdir, row['img_id'])).shape
        j['img_sz'] = {'width': width, 'height': height}
    else:
        j['img_sz'] = {'width': None, 'height': None}
    j['img_feature'] = None
    j['img_url'] = None
    return j


@eh.register(ce.ACTION_IMPORT_LABELS)
def pick_label(_):
    label_file = pick_file()
    if label_file is None:
        ce.emit(ce.ERROR_IMPORT_LABELS, now=True)
        return

    with open(label_file) as f:
        labels = f.readlines()
        labels = [label.replace(",", '').strip() for label in labels]
        labels = [label.replace('"', '').strip() for label in labels]
        labels = [label for label in labels if len(label) > 0]
        ce.emit(ce.SUCCESS_IMPORT_LABELS, labels=labels, now=True)


@eh.register(ce.ACTION_IMPORT_DATA)
def pick_data(_):
    file = pick_file()
    if file is None:
        ce.emit(ce.ERROR_IMPORT_DATA, now=True)
        return

    try:
        df = pd.read_csv(file)
    except Exception as e:
        ce.emit(ce.ERROR_IMPORT_DATA, error=e, now=True)
        return

    def hash_bbox(bboxes):
        return ['-'.join([str(i) for i in b]) for b in bboxes]

    def read_rel(rel):
        rel = rel.replace("|", ",")
        rel = literal_eval(rel)
        return rel

    df['img_texts'] = df['img_texts'].apply(literal_eval)
    df['img_bboxes'] = df['img_bboxes'].apply(literal_eval)
    df['img_bbox_hashes'] = df['img_bboxes'].apply(hash_bbox)
    try:
        df['rel_s'] = df['rel_s'].apply(read_rel)
        df['rel_g'] = df['rel_g'].apply(read_rel)
    except Exception:
        pass

    ce.emit(ce.SUCCESS_IMPORT_DATA, data=df, now=True)


@eh.register(ce.ACTION_SELECT_IMGDIR)
def pick_img_dir(_):
    d = pick_directory()
    if d is not None:
        ce.emit(ce.SUCCESS_SELECT_IMGDIR, imgdir=d, now=True)


@eh.register(ce.REQUEST_SAVE_SESSION)
def _(event):
    file = pick_save_file()
    if file is None:
        return

    if not file.endswith(".pkl"):
        file = file + ".pkl"

    try:
        with open(file, "wb") as f:
            pickle.dump(event.state, f)

        ce.emit(ce.SUCCESS_SAVE_SESSION, now=True)
    except Exception:
        traceback.print_exc()


@eh.register(ce.ACTION_LOAD_SESSION)
def _(event):
    file = pick_file()
    if file is None:
        return

    try:
        with open(file, 'rb') as f:
            state = pickle.load(f)

        ce.emit(ce.REQUEST_LOAD_SESSION, now=True, state=state)
    except Exception:
        traceback.print_exc()


@eh.register(ce.ACTION_EXPORT_JSON)
def export_data(event):
    state = event.state
    if state.data is None:
        return

    save_to = pick_save_file()
    if save_to is None:
        return

    if not save_to.endswith(".jsonl"):
        save_to = save_to + ".jsonl"

    # SORT FIELD_RS BY FIELD ORDER
    field_rs = []
    for field in state.labels:
        if field in state.labels_rs:
            field_rs.append(field)

    jl = ""
    for (i, row) in state.data.iterrows():
        j = data_to_json(row, state, field_rs)
        j = json.dumps(j, ensure_ascii=False)
        jl = f"{jl}\n{j}"

    with open(save_to, 'w') as f:
        f.write(jl.strip())


process_event = eh.process_event
