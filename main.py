import pygame as pg
import pygame.locals as lc
import libbuttons
from metadata import Label, Token, Menu
import utils
import pickle
import custom_events as ce
from states import State, REL_S_KEY, REL_G_KEY
import libio
import states
import os
import traceback
from argparse import Namespace
import theme
import drag

cache = Namespace()
cache.render_hash = None


def render(root, state):
    # CALCULATE STUFF
    rw, rh = root.get_rect().size

    new_render_hash = hash((rw, rh))
    mh = min(rh * 0.1, 32)
    sw = min(rh * 0.3, 200)

    # SET TITLE
    if state.data is not None and state.data_index is not None:
        n, _ = state.data.shape
        i = state.data_index
        pg.display.set_caption(f"{state.data.loc[i, 'img_id']} {i+1}/{n}")
        row = state.data.loc[i]
        row = pickle.dumps(row)
        new_render_hash = hash((rw, rh, row))

    root.fill((43, 43, 43))
    if new_render_hash != cache.render_hash or cache.render_hash is None:
        cache.sidebar_root = root.subsurface(pg.Rect(0, mh+1, sw, rh - mh-1))
        cache.mainview_root = root.subsurface(
            pg.Rect(sw, mh+1, (rw - sw), rh - mh - 1))
        cache.menu_root = root.subsurface(pg.Rect(0, 0, rw, mh))

    try:
        render_arrows(root, state)
    except KeyError:
        pass
    except Exception:
        traceback.print_exc()
    render_mainview(root, cache.mainview_root, state, new_render_hash)
    render_image(root, cache.mainview_root, state)
    render_sidebar(root, cache.sidebar_root, state)
    render_menu(root, cache.menu_root, state)
    cache.render_hash = new_render_hash

    # DRAW DRAGING REGION
    if drag.is_dragging():
        r = drag.drag_region()
        s = pg.Surface((r.w, r.h))
        s.set_alpha(125)
        s.fill(theme.btn_bg_selected)
        root.blit(s, (r.x, r.y))


def render_image(root, image_root, state):
    if state.data is None or state.imgdir is None:
        return

    df = state.data
    i = state.data_index
    imgdir = state.imgdir
    imgfile = df.loc[i, 'img_id']

    try:
        image = os.path.join(imgdir, imgfile)
        image = pg.image.load(image)
    except Exception as e:
        print("Can't load image: ", type(e))
        return

    dx, dy = image_root.get_offset()
    sw, sh = image_root.get_rect().size
    iw, ih = image.get_size()
    rx, ry = min(theme.max_image_width, theme.image_ratio * sw)/iw, sh/ih
    ratio = rx if rx < ry else ry
    image = pg.transform.scale(image, (int(iw * ratio), int(ih * ratio)))
    iw, ih = image.get_size()
    x = sw - iw
    y = sh - ih
    image_root.blit(image, (x, y))


def render_arrows(root, state):
    if state.data is None:
        return

    df = state.data
    i = state.data_index

    if REL_S_KEY not in df.columns or REL_G_KEY not in df.columns:
        return

    rel_s = df.loc[i, REL_S_KEY]
    rel_g = df.loc[i, REL_G_KEY]

    for (b1, b2) in rel_s.edges:
        if (b1, b2) in rel_g.edges:
            continue

        # if isinstance(b1, Label):
        #     continue
        # if isinstance(b2, Label):
        #     print("[Warning]",
        #           f"button {b2} is a label and at the end of an arrow")
        #     continue

        b1 = libbuttons.Button.get_button_by_meta(b1)
        b2 = libbuttons.Button.get_button_by_meta(b2)
        libbuttons.draw_line(root,
                             b1,
                             b2,
                             theme.rel_s_color, thickness=theme.arrow_thickness)

    for (b1, b2) in rel_g.edges:
        if (b1, b2) in rel_s.edges:
            continue
        b1 = libbuttons.Button.get_button_by_meta(b1)
        b2 = libbuttons.Button.get_button_by_meta(b2)
        libbuttons.draw_line(root,
                             b1,
                             b2,
                             theme.rel_g_color, thickness=theme.arrow_thickness)

    for (b1, b2) in rel_g.edges:
        if (b1, b2) not in rel_s.edges:
            continue
        b1 = libbuttons.Button.get_button_by_meta(b1)
        b2 = libbuttons.Button.get_button_by_meta(b2)
        libbuttons.draw_line(root,
                             b1,
                             b2,
                             theme.rel_both_color, thickness=theme.arrow_thickness)


def render_mainview(root, mainview_root, state, new_render_hash=None):
    if state.data is None:
        return

    df = state.data
    i = state.data_index
    texts = df.loc[i, 'img_texts']
    bboxes = df.loc[i, 'img_bboxes']
    bbox_hashes = df.loc[i, 'img_bbox_hashes']

    if cache.render_hash != new_render_hash or cache.render_hash is None:
        vbox = libbuttons.VBox(elems=[],
                               x=state.mainview_x_offset,
                               y=state.mainview_y_offset,
                               spacing=50)
        for row in utils.arrange_row(bboxes):
            hbox = libbuttons.HBox([], 0, 0, 50)
            for col in row:
                text = texts[col]
                bbox = bbox_hashes[col]
                btn = libbuttons.Button(surface=mainview_root,
                                        meta=Token(text, bbox),
                                        text=text)
                btn.prefix = btn.selected_prefix()
                hbox.append(btn)
            vbox.append(hbox)
            cache.mainview_buttons = vbox

    else:
        vbox = getattr(cache, 'mainview_buttons', None)

    if vbox is not None:
        for hbox in vbox.elems:
            for btn in hbox.elems:
                btn.prefix = btn.selected_prefix()
        vbox.x = state.mainview_x_offset
        vbox.y = state.mainview_y_offset
        vbox.draw()


def render_sidebar(root, sidebar_root, state):
    if state.labels is None:
        return

    label_btns = []
    for label in state.labels:
        btn = libbuttons.Button(
            meta=Label(label),
            text=label,
            x=0, y=0,
            width=sidebar_root.get_rect().width,
            surface=sidebar_root,
        )
        prefix = ""
        if label in state.labels_rs:
            prefix += "[R]"
        prefix += btn.selected_prefix()
        prefix = prefix.strip() + " "
        btn.prefix = prefix
        label_btns.append(btn)

    libbuttons.VBox(label_btns,
                    0,
                    state.sidebar_y_offset,
                    state.sidebar_y_spacing).draw()


def render_menu(root, menu_root, state):
    mh = menu_root.get_rect().height
    import_label = libbuttons.Button(
        meta=Menu("Import labels"),
        text="Import labels",
        height=mh,
        onclick=ce.emit(ce.ACTION_IMPORT_LABELS),
        surface=menu_root)

    import_data = libbuttons.Button(
        meta=Menu("Pick data"),
        text="Import data",
        height=mh,
        onclick=ce.emit(ce.ACTION_IMPORT_DATA),
        surface=menu_root)

    select_imgdir = libbuttons.Button(
        meta=Menu("Select IMG"),
        text="Select IMG dir",
        height=mh,
        onclick=ce.emit(ce.ACTION_SELECT_IMGDIR),
        surface=menu_root,
    )

    delete_record = libbuttons.Button(
        meta=Menu("Delete record"),
        text="Delete record",
        height=mh,
        onclick=ce.emit(ce.ACTION_DELETE_RECORD),
        surface=menu_root)

    save_session = libbuttons.Button(
        meta=Menu("Save session"),
        text="Save session",
        height=mh,
        onclick=ce.emit(ce.ACTION_SAVE_SESSION),
        surface=menu_root)

    load_session = libbuttons.Button(
        meta=Menu("Load session"),
        text="Load session",
        height=mh,
        onclick=ce.emit(ce.ACTION_LOAD_SESSION),
        surface=menu_root)

    export_data = libbuttons.Button(
        meta=Menu("Export data"),
        text="Export data",
        height=mh,
        onclick=ce.emit(ce.ACTION_EXPORT_JSON, state=state),
        surface=menu_root)

    import_jsonl = libbuttons.Button(
        meta=Menu("Import jsonl"),
        text="Import jsonl",
        height=mh,
        onclick=ce.emit(ce.ACTION_IMPORT_JSON),
        surface=menu_root)

    libbuttons.HBox([import_label,
                     import_data,
                     select_imgdir,
                     delete_record,
                     save_session,
                     load_session,
                     export_data,
                     import_jsonl], 0, 0, 1).draw()


def main(state):
    clock = pg.time.Clock()
    root = pg.display.set_mode((1280, 720), lc.RESIZABLE)

    while True:
        libbuttons.Button.reset_render_state()
        render(root, state)

        pg.event.pump()
        for event in pg.event.get():
            # DETECT BUTTON PRESS
            libbuttons.Button.process_event(event)
            libio.process_event(event)
            states.process_event(event, state)
            drag.process_event(event)

            # BUTTON PRESS
            if event.type == ce.BUTTON_PRESS:
                btn = event.button
                if isinstance(btn.meta, Menu):
                    cb = getattr(btn, 'onclick', None)
                    if cb is not None:
                        cb()
                elif isinstance(btn.meta, (Label, Token)):
                    libbuttons.Button.handle_selection(btn, state=state)

            # DRAG SELECTION
            if event.type == ce.ACTION_DRAG:
                region = event.region
                for btn in libbuttons.Button.buttons:
                    if pg.Rect.colliderect(btn.abs_rect, region) and isinstance(btn.meta, (Token, Label)):
                        libbuttons.Button.handle_selection(
                            btn, include=True, state=state)

            # SCROLL
            if event.type == lc.MOUSEWHEEL:
                scroll_speed = 20
                sgn = event.y
                if pg.key.get_mods() & lc.KMOD_SHIFT:
                    state.sidebar_y_offset += scroll_speed * sgn
                elif pg.key.get_mods() & lc.KMOD_ALT:
                    state.sidebar_y_spacing += scroll_speed * sgn // 10
                    if state.sidebar_y_spacing < 1:
                        state.sidebar_y_spacing = 1
                elif pg.key.get_mods() & lc.KMOD_CTRL:
                    state.mainview_x_offset += scroll_speed * sgn
                else:
                    state.mainview_y_offset += scroll_speed * sgn

            # KEYBOARD INPUT
            if event.type == lc.KEYDOWN:
                mods = pg.key.get_mods()
                offset_multiply = 10 if mods & lc.KMOD_SHIFT else 1
                if event.key == lc.K_d:
                    ce.emit(ce.ACTION_CHANGE_DATAINDEX,
                            offset=1 * offset_multiply,
                            now=True)
                if event.key == lc.K_a:
                    ce.emit(ce.ACTION_CHANGE_DATAINDEX,
                            offset=-1 * offset_multiply,
                            now=True)
                if event.key == lc.K_s:
                    fanout = pg.key.get_mods() & lc.KMOD_SHIFT
                    ce.emit(ce.ACTION_REL_S,
                            selection=libbuttons.Button.selection,
                            fanout=fanout,
                            now=True)
                if event.key == lc.K_g:
                    ce.emit(ce.ACTION_REL_G,
                            selection=libbuttons.Button.selection,
                            now=True)
                if event.key == lc.K_r:
                    ce.emit(ce.ACTION_REL_REMOVE,
                            selection=libbuttons.Button.selection,
                            now=True)
                if event.key == lc.K_c:
                    copy = pg.key.get_mods() & lc.KMOD_CTRL
                    if copy:
                        ce.emit(ce.ACTION_COPY,
                                selection=libbuttons.Button.selection,
                                now=True)
                    else:
                        ce.emit(ce.ACTION_LABEL_RS,
                                selection=libbuttons.Button.selection,
                                now=True)

            # QUIT
            if event.type == lc.QUIT:
                pg.quit()
                return

        # UPDATE DISPLAY
        pg.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    pg.init()
    pg.key.set_repeat(500, 100)
    state = State()
    from datetime import datetime
    try:
        main(state)
        now = datetime.now().strftime('%Y%m%d%H%M')
        with open(f"autosave-{now}.pkl", "wb") as f:
            pickle.dump(state, f)
    except Exception:
        traceback.print_exc()
        with open("emergency.pkl", "wb") as f:
            pickle.dump(state, f)
