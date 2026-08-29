"""Final assembly: moose_teardrop_profile.svg / .dxf, preview.png, spec.md."""
import numpy as np
from shapely.geometry import Point, LineString, box
from shapely.ops import unary_union
from racket_lib import (calibrated_outline, sample_spans, outline_polygon,
                        channel_polys, hole_centers, min_curvature_radius,
                        edge_x_at, HOLE_D, PERIM_SOLID, BRIDGE_TOP, SWEET_Y,
                        SWEET_R, PITCH_MAIN, PITCH_SWEET, HANDLE_LEN, HEAD_LEN,
                        TOTAL_LEN, HEAD_MAX_W)
import racket_svg as rs

CHANNEL = dict(width=7.5, y_open=249.0, overshoot=9.0,
               ctrl=[(34.0, 246.0), (24.0, 243.0), (19.0, 236.0), (18.25, 226.0)])

# ---------------- geometry -------------------------------------------------
spans, _ = calibrated_outline()
pts = sample_spans(spans, 80)
outline = outline_polygon(spans)
chR, chL, cl = channel_polys(pts, CHANNEL)
centers, allowed = hole_centers(outline, [chR, chL])
holes_geo = [Point(c).buffer(HOLE_D / 2, quad_segs=32) for c in centers]

# ---------------- metrics --------------------------------------------------
M = {}
M["len"] = pts[:, 1].max() - pts[:, 1].min()
M["width"] = 2 * pts[:, 0].max()
M["widest_y"] = float(pts[np.argmax(pts[:, 0]), 1])
M["widest_frac"] = (M["widest_y"] - HANDLE_LEN) / HEAD_LEN
hpts = pts[(pts[:, 1] < 190) & (pts[:, 0] > 0)]
M["handle_w"] = 2 * hpts[:, 0].max()
M["bridge_base_w"] = 2 * edge_x_at(pts, BRIDGE_TOP)
M["ch_area"] = chR.intersection(outline).area
M["muzzle"] = chR.distance(chL)
M["half_path"] = chR.distance(LineString([(0, 190), (0, 262)]))
M["r_min_inner"] = min_curvature_radius(np.asarray(cl.coords)) - CHANNEL["width"] / 2

cross = chR.exterior.intersection(outline.exterior)
corners = [np.array([g.x, g.y]) for g in
           (cross.geoms if cross.geom_type != "Point" else [cross])]
arm_min, wedge_reach = 1e9, 0.0
for y in np.arange(192, 262, 0.25):
    ex = edge_x_at(pts, y)
    d = chR.distance(Point(ex, y))
    dc = min(np.hypot(ex - c[0], y - c[1]) for c in corners)
    if d < 9.0:
        wedge_reach = max(wedge_reach, dc)
    if dc >= 12.0:
        arm_min = min(arm_min, d)
M["arm_min"] = arm_min
M["wedge_reach"] = wedge_reach

M["n_holes"] = len(centers)
M["n_sweet"] = sum(1 for c in centers if np.hypot(c[0], c[1] - SWEET_Y) <= SWEET_R)
cs = np.array(centers)
dmin = 1e9
for i in range(len(cs)):
    d = np.hypot(cs[:, 0] - cs[i, 0], cs[:, 1] - cs[i, 1]); d[i] = 1e9
    dmin = min(dmin, d.min())
M["web_min"] = dmin - HOLE_D
M["edge_margin"] = min(outline.exterior.distance(Point(c)) for c in centers) - HOLE_D / 2
M["ch_margin"] = min(unary_union([chR, chL]).distance(Point(c)) for c in centers) - HOLE_D / 2

face_poly = outline.intersection(box(-140, BRIDGE_TOP, 140, 460))
M["face_area"] = face_poly.area
M["holes_area"] = len(centers) * np.pi * (HOLE_D / 2) ** 2
M["holes_pct"] = 100 * M["holes_area"] / M["face_area"]
M["gross_area"] = outline.area

# balance (uniform 38 mm slab, uniform effective density -> area centroid)
solid_no_holes = outline.difference(chR).difference(chL)
solid = solid_no_holes.difference(unary_union(holes_geo))
solid_ref = outline.difference(unary_union(holes_geo))   # no bridge channels
M["net_area"] = solid.area
M["balance"] = solid.centroid.y
M["balance_ref"] = solid_ref.centroid.y
M["balance_shift"] = M["balance"] - M["balance_ref"]
RHO = 0.23  # g/cm^3 effective (see spec assumptions)
M["mass_est"] = solid.area / 100.0 * 3.8 * RHO

for k, v in M.items():
    print(f"{k:14s}: {v:.2f}" if isinstance(v, float) else f"{k:14s}: {v}")

# ---------------- SVG + PNG ------------------------------------------------
svg = rs.build_svg(spans, channels=[chR, chL],
                   holes=[(c, HOLE_D) for c in centers], dims=True,
                   title="moose teardrop padel profile - 1:1 mm")
rs.write_svg("moose_teardrop_profile.svg", svg)
rs.render_png("moose_teardrop_profile.svg", "preview.png", scale=2.2)
print("wrote moose_teardrop_profile.svg / preview.png")

# ---------------- DXF ------------------------------------------------------
import ezdxf
doc = ezdxf.new("R2010", setup=True)
doc.header["$INSUNITS"] = 4      # millimetres
doc.header["$MEASUREMENT"] = 1
msp = doc.modelspace()
for name, color in [("OUTLINE", 5), ("BRIDGE_CUTOUTS", 1), ("HOLES", 7),
                    ("HANDLE", 3), ("ANNOTATIONS", 8)]:
    doc.layers.add(name, color=color)

def add_closed_poly(coords, layer):
    msp.add_lwpolyline([(float(x), float(y)) for x, y in coords],
                       close=True, dxfattribs={"layer": layer})

add_closed_poly(sample_spans(spans, 60)[:-1], "OUTLINE")
add_closed_poly(list(chR.exterior.coords)[:-1], "BRIDGE_CUTOUTS")
add_closed_poly(list(chL.exterior.coords)[:-1], "BRIDGE_CUTOUTS")
for (x, y) in centers:
    r = HOLE_D / 2.0
    msp.add_lwpolyline([(x - r, y, 0, 0, 1.0), (x + r, y, 0, 0, 1.0)],
                       format="xyseb", close=True, dxfattribs={"layer": "HOLES"})
handle_poly = outline.intersection(box(-60, -5, 60, HANDLE_LEN))
add_closed_poly(list(handle_poly.exterior.coords)[:-1], "HANDLE")

ann = [
    (140, 440, "MOOSE TEARDROP PADEL PROFILE - UNITS MM - SCALE 1:1"),
    (140, 430, f"TOTAL {M['len']:.1f} (FIP MAX 455) / HEAD WIDTH {M['width']:.1f} (MAX 260)"),
    (140, 420, f"HANDLE {HANDLE_LEN:.0f} LONG (MAX 200), {M['handle_w']:.1f} AT THROAT (MAX 50)"),
    (140, 410, f"{M['n_holes']} HOLES DIA 11 CYLINDRICAL, HEX PITCH 17.5 / 16 IN SWEET ZONE"),
    (140, 400, "BRIDGE CUTOUTS: SUBTRACT FROM OUTLINE; BREAK MOUTH CORNERS R3 MIN"),
    (140, 390, "NO HOLES WITHIN 10 MM OF OUTLINE (BUMPER CHANNEL BAND)"),
    (140, 380, "THICKNESS 38 MM (NOT MODELLED IN 2D)"),
]
for x, y, t in ann:
    msp.add_text(t, dxfattribs={"layer": "ANNOTATIONS", "height": 4.0,
                                "insert": (x, y)})
doc.saveas("moose_teardrop_profile.dxf")
print("wrote moose_teardrop_profile.dxf")

import json
json.dump({k: (float(v) if isinstance(v, (int, float, np.floating)) else v)
           for k, v in M.items()}, open("metrics.json", "w"), indent=1)
