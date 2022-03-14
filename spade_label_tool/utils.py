import numpy as np


TWO_COORD_FORMAT = 0
FOUR_COORD_FORMAT = 1


def detect_bbox_format(bbox):
    if isinstance(bbox[0], int):
        return TWO_COORD_FORMAT
    else:
        return FOUR_COORD_FORMAT


def hash_bboxes(bboxes):
    """
    return unsafe hash of list of bounding boxes

    Parameter:
    ---
    bboxes: list
        list of bounding boxes
    """
    return [b.hash for b in bboxes]
    # def hash_single_bbox(bbox):
    #     if detect_bbox_format(bbox) == FOUR_COORD_FORMAT:
    #         bbox = coord_to_bbox(bbox)
    #     return '-'.join([str(i) for i in bbox])
    # return [hash_single_bbox(b) for b in bboxes]


def bbox_to_coord(b):
    '''
    bbox x1, x2, y1, y2 format -> 4-coordinate format
    '''
    x1, x2, y1, y2 = b
    return [[x1, y1],
            [x2, y1],
            [x2, y2],
            [x1, y2]]


def coord_to_bbox(coords, batch=False):
    '''
    bbox 4-coordinate format -> x1, x2, y1, y2 format
    '''
    if batch:
        return [coord_to_bbox(c) for c in coords]
    x = [p[0] for p in coords]
    y = [p[1] for p in coords]
    return min(x), max(x), min(y), max(y)


def arrange_bbox(bboxes):
    n = len(bboxes)
    xcentres = [b.center_x for b in bboxes]
    ycentres = [b.center_y for b in bboxes]
    heights = [b.height for b in bboxes]
    width = [b.width for b in bboxes]

    def is_top_to(i, j):
        result = (ycentres[j] - ycentres[i]) > ((heights[i] + heights[j]) / 3)
        return result

    def is_left_to(i, j):
        return (xcentres[i] - xcentres[j]) > ((width[i] + width[j]) / 3)

    # <L-R><T-B>
    # +1: Left/Top
    # -1: Right/Bottom
    g = np.zeros((n, n), dtype='int')
    for i in range(n):
        for j in range(n):
            if is_left_to(i, j):
                g[i, j] += 10
            if is_left_to(j, i):
                g[i, j] -= 10
            if is_top_to(i, j):
                g[i, j] += 1
            if is_top_to(j, i):
                g[i, j] -= 1
    return g


def arrange_row(bboxes=None, g=None, i=None, visited=None):
    if visited is not None and i in visited:
        return []
    if g is None:
        g = arrange_bbox(bboxes)
    if i is None:
        visited = []
        rows = []
        for i in range(g.shape[0]):
            if i not in visited:
                indices = arrange_row(g=g, i=i, visited=visited)
                visited.extend(indices)
                rows.append(indices)
        return rows
    else:
        indices = [j for j in range(g.shape[0]) if j not in visited]
        indices = [j for j in indices if abs(g[i, j]) == 10 or i == j]
        indices = np.array(indices)
        g_ = g[np.ix_(indices, indices)]
        order = np.argsort(np.sum(g_, axis=1))
        indices = indices[order].tolist()
        indices = [int(i) for i in indices]
        return indices
