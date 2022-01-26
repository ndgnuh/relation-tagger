from argparse import Namespace

theme = Namespace()

#
# BUTTONS
#
theme.btn_fg_normal = (66, 66, 66)
theme.btn_bg_normal = (255, 255, 255)
# SELECTED
theme.btn_fg_selected = (33, 33, 33)
theme.btn_bg_selected = (100, 255, 255)
# HOVER
theme.btn_fg_hover = (0, 0, 0)
theme.btn_bg_hover = (228, 230, 235)

# IMAGE
theme.max_image_width = 99999
theme.image_ratio = 0.3

# ARROWS
theme.rel_g_color = (255, 100, 100)
theme.rel_s_color = (100, 100, 255)
theme.rel_both_color = (255, 100, 255)


def __getattr__(key):
    return getattr(theme, key)
