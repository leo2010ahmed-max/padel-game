"""Geometry library for the moose-teardrop padel racket profile.

Coordinate system (design space):
    units: mm
    y = 0 at the handle butt, +y toward the crown
    x = 0 on the centreline, mirror symmetric

The outline is a closed uniform periodic cubic B-spline (C2 continuous,
hence G2) defined by a mirror-symmetric control polygon and converted
exactly to cubic Bezier spans.
"""

import math
import numpy as np
from shapely.geometry import Polygon, LineString, Point, MultiPolygon
from shapely.ops import unary_union

# ----------------------------------------------------------------------------
# regulatory / design targets (mm)
# ----------------------------------------------------------------------------
TOTAL_LEN = 453.0          # target (FIP hard limit 455)
HANDLE_LEN = 190.0         # target (FIP hard limit 200)
HEAD_LEN = TOTAL_LEN - HANDLE_LEN   # 263
HEAD_MAX_W = 257.0         # target (FIP hard limit 260)
HANDLE_W_THROAT = 45.0     # target (FIP hard limit 50)
WIDEST_FRAC = 0.61         # widest point at 61 % of head length from throat
BRIDGE_TOP = 260.0         # y where the face starts (bridge is 190..260, 70 tall)
PERIM_SOLID = 10.0         # frame / bumper channel band, no holes
HOLE_D = 11.0
SWEET_Y = HANDLE_LEN + 0.55 * HEAD_LEN   # 334.65
SWEET_R = 42.0
PITCH_MAIN = 17.5
PITCH_SWEET = 16.0


# ----------------------------------------------------------------------------
# closed uniform cubic B-spline -> exact cubic Bezier spans
# ----------------------------------------------------------------------------
def bspline_to_beziers(ctrl):
    """ctrl: list of (x, y) control points of a closed uniform cubic B-spline.
    Returns list of Bezier spans [(b0, b1, b2, b3), ...] (numpy arrays),
    exactly equivalent to the spline, C2/G2 continuous, closed."""
    P = [np.asarray(p, dtype=float) for p in ctrl]
    n = len(P)
    spans = []
    for i in range(n):
        p0, p1, p2, p3 = P[i], P[(i + 1) % n], P[(i + 2) % n], P[(i + 3) % n]
        b0 = (p0 + 4 * p1 + p2) / 6.0
        b1 = (4 * p1 + 2 * p2) / 6.0
        b2 = (2 * p1 + 4 * p2) / 6.0
        b3 = (p1 + 4 * p2 + p3) / 6.0
        spans.append((b0, b1, b2, b3))
    return spans


def bezier_point(span, t):
    b0, b1, b2, b3 = span
    mt = 1 - t
    return (mt ** 3) * b0 + 3 * (mt ** 2) * t * b1 + 3 * mt * (t ** 2) * b2 + (t ** 3) * b3


def sample_spans(spans, per_span=40):
    pts = []
    for s in spans:
        for k in range(per_span):
            pts.append(bezier_point(s, k / per_span))
    pts.append(pts[0])
    return np.array(pts)


# ----------------------------------------------------------------------------
# outline control polygon
# ----------------------------------------------------------------------------
def outline_controls(dy_bot=0.0, dy_top=0.0, sx_wide=1.0):
    """Right-hand-side control points bottom->top; mirrored automatically."""
    right = [
        (12.0, -2.0 + dy_bot),
        (20.5, 2.0 + dy_bot * 0.5),
        (21.0, 40.0),
        (21.7, 100.0),
        (22.2, 160.0),
        (22.1, 184.0),
        (22.85, 203.0),
        (34.0, 224.0),
        (49.0, 244.0),
        (63.0, 262.0),
        (95.0, 290.0),
        (121.0 * sx_wide, 318.0),
        (131.5 * sx_wide, 344.0),
        (127.0 * sx_wide, 370.0),
        (110.0, 404.0),
        (82.0, 436.0 + dy_top * 0.5),
        (45.0, 452.0 + dy_top),
        (0.0, 458.0 + dy_top),
    ]
    ctrl = [(0.0, -2.0 + dy_bot)] + right
    # mirror (skip the two centreline points)
    for x, y in reversed(right[:-1]):
        ctrl.append((-x, y))
    return ctrl


def calibrated_outline():
    """Iteratively nudge control points so the curve hits the targets."""
    dy_bot, dy_top, sx = 0.0, 0.0, 1.0
    spans = None
    for _ in range(40):
        ctrl = outline_controls(dy_bot, dy_top, sx)
        spans = bspline_to_beziers(ctrl)
        pts = sample_spans(spans, 60)
        ymin, ymax = pts[:, 1].min(), pts[:, 1].max()
        xmax = pts[:, 0].max()
        dy_bot += (0.0 - ymin)
        dy_top += (TOTAL_LEN - ymax)
        sx *= (HEAD_MAX_W / 2.0) / xmax
        if abs(ymin) < 5e-4 and abs(ymax - TOTAL_LEN) < 5e-4 and \
           abs(xmax - HEAD_MAX_W / 2.0) < 5e-4:
            break
    return spans, (dy_bot, dy_top, sx)


def outline_polygon(spans, per_span=60):
    pts = sample_spans(spans, per_span)
    return Polygon(pts).buffer(0)


def edge_x_at(pts, y):
    """x of the right-hand outline at height y (single-valued in the throat)."""
    right = pts[pts[:, 0] > 0]
    order = np.argsort(right[:, 1])
    return float(np.interp(y, right[order][:, 1], right[order][:, 0]))


# ----------------------------------------------------------------------------
# bridge channels (moose antler inner edges)
# ----------------------------------------------------------------------------
def cubic_points(p0, p1, p2, p3, n=120):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2, p3 = map(lambda p: np.asarray(p, float), (p0, p1, p2, p3))
    return ((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 +
            3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3)


def open_bspline_points(ctrl, per_span=30):
    """Clamped open uniform cubic B-spline through the end points (C2)."""
    P = [np.asarray(p, float) for p in ctrl]
    P = [P[0], P[0]] + P + [P[-1], P[-1]]
    pts = []
    for i in range(len(P) - 3):
        p0, p1, p2, p3 = P[i], P[i + 1], P[i + 2], P[i + 3]
        b0 = (p0 + 4 * p1 + p2) / 6.0
        b1 = (4 * p1 + 2 * p2) / 6.0
        b2 = (2 * p1 + 4 * p2) / 6.0
        b3 = (p1 + 4 * p2 + p3) / 6.0
        for k in range(per_span):
            t = k / per_span
            mt = 1 - t
            pts.append(mt ** 3 * b0 + 3 * mt ** 2 * t * b1 +
                       3 * mt * t ** 2 * b2 + t ** 3 * b3)
    pts.append(P[-1])
    return np.array(pts)


def channel_polys(outline_pts, params):
    """Two mirrored channels. The centreline starts outside the outline along
    the local outward edge normal (genuinely open to the throat edge), then
    sweeps inward and downward through the given waypoints."""
    w = params["width"]
    y0 = params["y_open"]
    ex = edge_x_at(outline_pts, y0)
    tx_ = edge_x_at(outline_pts, y0 + 2.0) - edge_x_at(outline_pts, y0 - 2.0)
    t = np.array([tx_, 4.0]); t /= np.linalg.norm(t)
    n = np.array([t[1], -t[0]])          # outward normal
    E = np.array([ex, y0])
    ctrl = [E + n * params["overshoot"]] + [np.asarray(p, float)
                                            for p in params["ctrl"]]
    cl = LineString(open_bspline_points(ctrl, per_span=40))
    right = cl.buffer(w / 2.0, quad_segs=48)
    left = Polygon([(-x, y) for x, y in right.exterior.coords])
    return right, left, cl


def min_curvature_radius(pts):
    p = np.asarray(pts)
    d1 = np.gradient(p, axis=0)
    d2 = np.gradient(d1, axis=0)
    num = np.abs(d1[:, 0] * d2[:, 1] - d1[:, 1] * d2[:, 0])
    den = (d1[:, 0] ** 2 + d1[:, 1] ** 2) ** 1.5
    with np.errstate(divide="ignore", invalid="ignore"):
        k = num / den
    k = k[np.isfinite(k)]
    return 1.0 / k.max() if k.max() > 0 else float("inf")


# ----------------------------------------------------------------------------
# hole grid
# ----------------------------------------------------------------------------
def hex_grid(pitch, center, y_range, x_range):
    cx, cy = center
    rows = []
    dy = pitch * math.sqrt(3) / 2.0
    j0 = int(math.floor((y_range[0] - cy) / dy)) - 1
    j1 = int(math.ceil((y_range[1] - cy) / dy)) + 1
    for j in range(j0, j1 + 1):
        y = cy + j * dy
        off = (pitch / 2.0) if (j % 2) else 0.0
        i0 = int(math.floor((x_range[0] - cx - off) / pitch)) - 1
        i1 = int(math.ceil((x_range[1] - cx - off) / pitch)) + 1
        for i in range(i0, i1 + 1):
            rows.append((cx + off + i * pitch, y))
    return rows


def hole_centers(outline_poly, channels, y_min_center=266.0):
    """Hex layout: 16 mm pitch inside the sweet circle, 17.5 mm outside."""
    allowed = outline_poly.buffer(-(PERIM_SOLID + HOLE_D / 2.0))
    ch_union = unary_union(list(channels))
    xr = (-140, 140)
    yr = (y_min_center, TOTAL_LEN)
    sweet = Point(0, SWEET_Y)
    inner = [c for c in hex_grid(PITCH_SWEET, (0, SWEET_Y), yr, xr)
             if math.hypot(c[0], c[1] - SWEET_Y) <= SWEET_R]
    outer = [c for c in hex_grid(PITCH_MAIN, (0, SWEET_Y), yr, xr)
             if math.hypot(c[0], c[1] - SWEET_Y) > SWEET_R]
    # drop outer holes that crowd inner ones (keep webs >= 4 mm)
    keep_outer = []
    for c in outer:
        if all(math.hypot(c[0] - d[0], c[1] - d[1]) >= HOLE_D + 4.0 for d in inner):
            keep_outer.append(c)
    centers = []
    for c in inner + keep_outer:
        p = Point(c)
        if c[1] < y_min_center:
            continue
        if not allowed.contains(p):
            continue
        if ch_union.distance(p) < HOLE_D / 2.0 + 9.0:   # >=9 mm solid to channel
            continue
        centers.append(c)
    return centers, allowed
