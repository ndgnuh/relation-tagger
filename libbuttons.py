from typing import List, Dict, Union, Optional, Callable
import pygame as pg
import pygame.locals as lc
import theme
from functools import cache
from metadata import Label, Token, Menu
import custom_events as ce


def emit_signal(button):
    args = {"button": button}
    event = pg.event.Event(ce.BUTTON_PRESS, args)
    pg.event.post(event)


@cache
def get_default_font():
    font = pg.font.SysFont('sans', 14)
    return font


class Button:
    buttons: List = []
    buttons_by_hash: Dict = {}
    buttons_hover: Dict = {}
    selection: List = []
    label_selection: List = []

    @classmethod
    def get_button_by_meta(cls, meta):
        b = cls.buttons_by_hash[hash(meta)]
        b = cls.buttons[b]
        return b

    def __new__(cls, meta, *args, **kwargs):
        h = hash(meta)
        if h in Button.buttons_by_hash:
            return Button.buttons[Button.buttons_by_hash[h]]
        else:
            btn = super(Button, cls).__new__(cls)
            Button.buttons.append(btn)
            Button.buttons_by_hash[h] = Button.buttons.index(btn)
            return btn

    def __init__(self,
                 text: str,
                 surface: pg.Surface,
                 meta: Union[Label, Token, Menu],
                 x: int = 0,
                 y: int = 0,
                 width: Optional[int] = None,
                 height: Optional[int] = None,
                 padding: int = 5,
                 prefix: str = "",
                 postfix: str = "",
                 selected: bool = False,
                 bg_normal: tuple = theme.btn_bg_normal,
                 fg_normal: tuple = theme.btn_fg_normal,
                 bg_hover: tuple = theme.btn_bg_hover,
                 fg_hover: tuple = theme.btn_fg_hover,
                 bg_selected: tuple = theme.btn_bg_selected,
                 fg_selected: tuple = theme.btn_fg_selected,
                 onclick: Optional[Callable] = None):
        self.text = text
        self.surface = surface
        self.meta = meta
        self.x = x
        self.y = y
        self.prefix = ""
        self.postfix = ""
        self.padding = padding
        self.bg_normal: tuple = theme.btn_bg_normal
        self.fg_normal: tuple = theme.btn_fg_normal
        self.bg_hover: tuple = theme.btn_bg_hover
        self.fg_hover: tuple = theme.btn_fg_hover
        self.bg_selected: tuple = theme.btn_bg_selected
        self.fg_selected: tuple = theme.btn_fg_selected
        self.bg_label_selected: tuple = theme.btn_bg_label_selected
        self.fg_label_selected: tuple = theme.btn_fg_label_selected
        self.selected = selected
        self.width = width
        self.height = height
        self.onclick = onclick
        self.rendered = False

    @property
    def fulltext(self):
        return self.prefix + self.text + self.postfix

    @property
    def rect(s):
        return pg.Rect(s.x, s.y, s.total_width, s.total_height)

    @property
    def abs_rect(s):
        dx, dy = s.surface.get_offset()
        return pg.Rect(s.x + dx, s.y + dy, s.total_width, s.total_height)

    @property
    def total_width(s):
        font = get_default_font()
        txt = font.render(s.fulltext, True, (0, 0, 0))
        if s.width is None:
            return txt.get_width() + 2 * s.padding
        else:
            return s.width
        return

    @property
    def total_height(s):
        txt = get_default_font().render(s.fulltext, True, (0, 0, 0))
        if s.height is None:
            return txt.get_height() + 2 * s.padding
        else:
            return s.height
        return

    @property
    def is_hovered(self):
        x, y = pg.mouse.get_pos()
        dx, dy = self.surface.get_offset()
        return self.rect.collidepoint(x - dx, y - dy)

    @property
    def is_selected(self):
        return self in self.__class__.selection

    @property
    def is_label_selected(self):
        return self.meta in self.__class__.label_selection

    def selected_prefix(self):
        if self.is_selected:
            cls = self.__class__
            index = cls.selection.index(self)
            return f"[{index + 1}] "
        else:
            return ""

    def __hash__(self):
        return hash(self.meta)

    def draw(self, xoffset=0, yoffset=0):
        dx, dy = self.surface.get_offset()
        # Auto color
        if self.is_selected:
            bg = self.bg_selected
            fg = self.fg_selected
        elif self.is_hovered:
            bg = self.bg_hover
            fg = self.fg_hover
        elif self.is_label_selected:
            bg = self.bg_label_selected
            fg = self.fg_label_selected
        else:
            bg = self.bg_normal
            fg = self.fg_normal

        pg.draw.rect(self.surface, bg, self.rect)
        txt = get_default_font().render(self.fulltext, True, fg)
        txt_x = self.x + self.padding + xoffset
        txt_y = self.y + self.padding + yoffset
        self.surface.blit(txt, (txt_x, txt_y))
        self.rendered = True

    # MARK BUTTONS AS NOT RENDERED
    # TO NOT MISCLICK
    @classmethod
    def reset_render_state(cls):
        for btn in cls.buttons:
            btn.rendered = False

    @classmethod
    def process_event(cls, event):
        # DETECT WHICH BTN WAS PRESSED
        if event.type == lc.MOUSEBUTTONUP and event.button == 1:
            x, y = event.pos
            btns = [btn for btn in cls.buttons if btn.rendered]
            for btn in btns:
                dx, dy = btn.surface.get_offset()
                if btn.rect.collidepoint(x - dx, y - dy):
                    emit_signal(btn)
                    print(f"Button {btn.meta} clicked")

        # CLEAN BUTTONS WHEN DATA INDEX CHANGE
        if event.type in [ce.ACTION_CHANGE_DATAINDEX,
                          ce.SUCCESS_REL_S,
                          ce.SUCCESS_REL_G,
                          ce.SUCCESS_REL_REMOVE,
                          ce.SUCCESS_LABEL_RS]:
            cls.selection = []

        if event.type == lc.MOUSEBUTTONUP and event.button == 3:
            cls.selection = []
            cls.label_selection = []

    @classmethod
    def handle_selection(cls, btn, include=False, state=None):
        if btn in cls.selection:
            if not include:
                cls.selection.remove(btn)
        elif btn.rendered:
            cls.selection.append(btn)

        # print("Handle selection, btn.meta", btn.meta)
        if isinstance(btn.meta, Label):
            for b in cls.selection:
                if b != btn and isinstance(b.meta, Label):
                    cls.selection.remove(b)

            cls.label_selection = []

            if btn.is_selected:
                df = state.data
                i = state.data_index

                REL_S_KEY = 'graph_s'
                if REL_S_KEY not in df.columns:
                    return

                rel_s = df.loc[i, REL_S_KEY]

                for b1, b2 in rel_s.edges:
                    if b1 == btn.meta:
                        cls.label_selection.append(b2)
            # print(cls.label_selection)


class Box:
    boxes_by_hash: Dict = {}

    # def __new__(cls, elems: List,
    #             x: int,
    #             y: int,
    #             spacing: int = 0):
    #     re

    def __hash__(self):
        hashes = [hash(e) for e in self.elems]
        hashes = '-'.join([str(h) for h in hashes])
        return hash(hashes)

    def __init__(self,
                 elems: List,
                 x: int,
                 y: int,
                 spacing: int = 0):
        self.elems = elems
        self.x = x
        self.y = y
        self.spacing = spacing
#     def __new__(cls, *args, **kwargs):
#         super


class HBox(Box):

    @property
    def total_width(self):
        w = 0
        for e in self.elems:
            w += e.total_width

        w += self.spacing * (len(self.elems) - 1)
        return w

    @property
    def total_height(self):
        return max(e.total_height for e in self.elems)

    def draw(self, x=None, y=None):
        elems = self.elems
        x = self.x if x is None else x
        y = self.y if y is None else y
        for elem in elems:
            elem.x = x
            elem.y = y
            x = x + elem.total_width + self.spacing
            elem.draw()

    def append(self, e):
        self.elems.append(e)


class VBox(Box):

    def append(self, e):
        self.elems.append(e)

    @property
    def total_height(self):
        w = 0
        for e in self.elems:
            w += e.total_height

        w += self.spacing * (len(self.elems) - 1)
        return w

    @property
    def total_width(self):
        return max(e.total_width for e in self.elems)

    def draw(self, x=None, y=None):
        elems = self.elems
        x = self.x if x is None else x
        y = self.y if y is None else y
        for elem in elems:
            elem.x = x
            elem.y = y
            y = y + elem.total_height + self.spacing
            elem.draw()


def align_vbox(btns, x, y, spacing=0):
    for btn in btns:
        btn.y = y
        btn.x = x
        y = y + btn.total_height + spacing


def draw_line(display, b1, b2, color, thickness=2):
    import math

    poss = {}
    poss[0] = ['center', 'center']
    poss[10] = ['midtop', 'midbottom']
    poss[1] = ['midleft', 'midright']
    poss[11] = ['topleft', 'bottomright']
    poss[9] = ['topright', 'bottomleft']

    for (k, v) in poss.copy().items():
        poss[-k] = list(reversed(v))

    def endpoint(b1, b2):
        # OFFSETS
        dx1, dy1 = b1.surface.get_offset()
        dx2, dy2 = b2.surface.get_offset()

        # CENTRES
        cx1, cy1 = b1.rect.center
        cx2, cy2 = b2.rect.center
        w1, w2 = b1.total_width, b2.total_width
        h1, h2 = b1.total_height, b2.total_height

        pos = 0
        if cy1 == cy2:
            if cx1 > cx2:
                x1, y1 = b1.rect.midright
                x2, y2 = b2.rect.midleft
            else:
                x1, y1 = b1.rect.midleft
                x2, y2 = b2.rect.midright
            return x1, x2, y1, y2
        else:
            if cx1 > cx2:
                pos += 1
            else:
                pos -= 1

        pos1, pos2 = poss[pos]
        x1, y1 = getattr(b1.rect, pos1)
        x2, y2 = getattr(b2.rect, pos2)
        if isinstance(b1.meta, Label):
            x1, y1 = b1.rect.midright
        if isinstance(b2.meta, Label):
            x2, y2 = b2.rect.midright
        return x1, x2, y1, y2

    def draw_arrow(screen, colour, start, end):
        head_size = 5
        pg.draw.line(screen, colour, start, end, thickness)
        rotation = math.degrees(math.atan2(
            start[1]-end[1], end[0]-start[0]))+90
        x1 = end[0]+head_size*math.sin(math.radians(rotation))
        y1 = end[1]+head_size*math.cos(math.radians(rotation))
        x2 = end[0]+head_size*math.sin(math.radians(rotation-120))
        y2 = end[1]+head_size*math.cos(math.radians(rotation-120))
        x3 = end[0]+head_size*math.sin(math.radians(rotation+120))
        y3 = end[1]+head_size*math.cos(math.radians(rotation+120))
        pg.draw.polygon(screen, color, ((x1, y1),
                                        (x2, y2), (x3, y3)))

    def get_xy(b):
        if isinstance(b.meta, Label):
            x, y = b.rect.midright
        else:
            x, y = b.rect.center
        dx, dy = b.surface.get_offset()
        return x + dx, y + dy

    x1, y1 = get_xy(b1)
    x2, y2 = get_xy(b2)
    xm = (x1 * 0.5 + x2 * 0.5)
    ym = (y1 * 0.5 + y2 * 0.5)
    draw_arrow(display, color, (x1, y1), (xm, ym))
    pg.draw.line(display, color, (xm, ym), (x2, y2), thickness)
