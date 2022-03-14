from ast import literal_eval
from spade_label_tool.metadata import Label, Token, Graph
from spade_label_tool import custom_events as ce
from spade_label_tool.utils import bbox_to_coord, hash_bboxes, coord_to_bbox
from pandas import DataFrame
import tkinter as tk
import tkinter.filedialog as filedialog
import pandas as pd
import traceback
import pickle
import json
import cv2
import os
import pygame as pg

REL_S_KEY = 'graph_s'
REL_G_KEY = 'graph_g'
eh = ce.EventHandler()


def tk_dialog(dl, **kwargs):
    root = tk.Tk()
    root.withdraw()
    return dl(**kwargs)


def pick_file(**kwargs):
    file = tk_dialog(filedialog.askopenfile)
    if file is None:
        return file
    file.close()
    name = file.name
    return name


def pick_save_file(**kwargs):
    name = tk_dialog(filedialog.asksaveasfilename)
    return name


def pick_directory():
    d = tk_dialog(filedialog.askdirectory)
    return d


def data_to_json(row, state, field_rs):
    j = {}
    j['data_id'] = row['img_id']
    j['fields'] = state.labels
    j['field_rs'] = field_rs
    j['text'] = list(row['img_texts'])
    j['label'] = [
        row[REL_S_KEY].adj.tolist(),
        row[REL_G_KEY].adj.tolist()]
    # print('n rel_g: ', len(row[REL_G_KEY].edges))
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
    label_file = pick_file(title="Pick label file")
    if label_file is None:
        ce.emit(ce.ERROR_IMPORT_LABELS, now=True)
        return

    with open(label_file, encoding='utf8') as f:
        labels = f.readlines()
        labels = [label.replace(",", '').strip() for label in labels]
        labels = [label.replace('"', '').strip() for label in labels]
        labels = [label for label in labels if len(label) > 0]
        ce.emit(ce.SUCCESS_IMPORT_LABELS, labels=labels, now=True)


@eh.register(ce.ACTION_IMPORT_DATA)
def pick_data(_):
    file = pick_file(title="Pick data file")
    if file is None:
        ce.emit(ce.ERROR_IMPORT_DATA, now=True)
        return

    try:
        df = pd.read_csv(file)
    except Exception as e:
        ce.emit(ce.ERROR_IMPORT_DATA, error=e, now=True)
        return

    def read_rel(rel):
        rel = rel.replace("|", ",")
        rel = literal_eval(rel)
        return rel

    df['img_texts'] = df['img_texts'].apply(literal_eval)
    df['img_bboxes'] = df['img_bboxes'].apply(literal_eval)
    df['img_bbox_hashes'] = df['img_bboxes'].apply(hash_bboxes)
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
    file = pick_save_file(title="Save session")
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
    file = pick_file(title="Pick session file")
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

    save_to = pick_save_file(title="Save jsonl")
    if save_to is None:
        return

    if not save_to.endswith(".jsonl"):
        save_to = save_to + ".jsonl"

    # SORT FIELD_RS BY FIELD ORDER
    field_rs = []
    for field in state.labels:
        if field in state.labels_rs:
            field_rs.append(field)

    # STATUS UPDATE
    old_caption, _ = pg.display.get_caption()
    jl = ""
    n = state.data.shape[0]
    for (i, row) in state.data.iterrows():
        j = data_to_json(row, state, field_rs)
        pg.display.set_caption(f"Dumping data {i+1}/{n}")
        j = json.dumps(j, ensure_ascii=False)
        jl = f"{jl}\n{j}"
    pg.display.set_caption(old_caption)

    with open(save_to, 'w', encoding='utf8') as f:
        f.write(jl.strip())


@eh.register(ce.ACTION_IMPORT_JSON)
def import_jsonl(event):
    file = pick_file(title="Pick jsonl file")

    if file is None:
        return

    with open(file, 'r', encoding='utf8') as f:
        data = [json.loads(s) for s in f.readlines()]
        # ['data_id', 'fields', 'field_rs', 'text',
        # 'label', 'coord', 'vertical', 'img_sz',
        # 'img_feature', 'img_url'])
        labels = data[0]['fields']
        labels_rs = data[0]['field_rs']
        img_ids = [j['data_id'] for j in data]
        img_texts = [j['text'] for j in data]
        img_bboxes = [coord_to_bbox(j['coord'], batch=True) for j in data]
        img_bbox_hashes = [hash_bboxes(bs) for bs in img_bboxes]
        s_graphs = [Graph(labels=labels,
                          bboxes=img_bbox_hashes[i],
                          texts=img_texts[i],
                          adj=j['label'][0],
                          text_first=False)
                    for (i, j) in enumerate(data)]
        g_graphs = [Graph(labels=labels,
                          bboxes=img_bbox_hashes[i],
                          texts=img_texts[i],
                          adj=j['label'][1],
                          text_first=False)
                    for (i, j) in enumerate(data)]

    df = DataFrame({
        'img_id': img_ids,
        'img_texts': img_texts,
        'img_bboxes': img_bboxes,
        'img_bbox_hashes': img_bbox_hashes,
        'graph_s': s_graphs,
        'graph_g': g_graphs,
    })
    ce.emit(ce.SUCCESS_IMPORT_DATA, data=df, now=True)
    ce.emit(ce.SUCCESS_IMPORT_LABELS, labels=labels,
            labels_rs=labels_rs, now=True)


process_event = eh.process_event
