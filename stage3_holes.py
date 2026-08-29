import numpy as np
from shapely.geometry import Point
from shapely.ops import unary_union
from racket_lib import (calibrated_outline, sample_spans, outline_polygon,
                        channel_polys, hole_centers, HOLE_D, PERIM_SOLID,
                        BRIDGE_TOP, SWEET_Y, SWEET_R)
import racket_svg as rs

CHANNEL = dict(width=7.5, y_open=249.0, overshoot=9.0,
               ctrl=[(34.0, 246.0), (24.0, 243.0), (19.0, 236.0), (18.25, 226.0)])

spans, _ = calibrated_outline()
pts = sample_spans(spans, 80)
outline = outline_polygon(spans)
chR, chL, cl = channel_polys(pts, CHANNEL)

centers, allowed = hole_centers(outline, [chR, chL])

# verification
min_edge = min(outline.exterior.distance(Point(c)) for c in centers) - HOLE_D / 2
min_ch = min(unary_union([chR, chL]).distance(Point(c)) for c in centers) - HOLE_D / 2
dmin = 1e9
cs = np.array(centers)
for i in range(len(cs)):
    d = np.hypot(cs[:, 0] - cs[i, 0], cs[:, 1] - cs[i, 1])
    d[i] = 1e9
    dmin = min(dmin, d.min())

face_area = outline.intersection(
    Point(0, 0).buffer(0).union(outline).difference(
        outline)  # placeholder
).area
# face = outline region above the bridge top
from shapely.geometry import box
face_poly = outline.intersection(box(-140, BRIDGE_TOP, 140, 460))
holes_area = len(centers) * np.pi * (HOLE_D / 2) ** 2
n_sweet = sum(1 for c in centers if np.hypot(c[0], c[1] - SWEET_Y) <= SWEET_R)

print(f"holes: {len(centers)}  (sweet-spot zone: {n_sweet})")
print(f"min web between holes         : {dmin - HOLE_D:.2f} mm (center spacing {dmin:.2f})")
print(f"min hole edge -> outline      : {min_edge:.2f} mm (need >= {PERIM_SOLID})")
print(f"min hole edge -> channel      : {min_ch:.2f} mm (need >= 9)")
print(f"face area (above bridge top)  : {face_poly.area:.0f} mm^2")
print(f"holes area                    : {holes_area:.0f} mm^2 "
      f"({100 * holes_area / face_poly.area:.1f} % of face removed)")
print(f"symmetry: {all(any(abs(c[0] + d[0]) < 1e-6 and abs(c[1] - d[1]) < 1e-6 for d in centers) for c in centers)}")

svg = rs.build_svg(spans, channels=[chR, chL],
                   holes=[(c, HOLE_D) for c in centers], dims=True,
                   title="stage 3 - holes")
rs.write_svg("iteration_stage3_holes.svg", svg)
rs.render_png("iteration_stage3_holes.svg", "preview_stage3.png")
print("wrote iteration_stage3_holes.svg / preview_stage3.png")
