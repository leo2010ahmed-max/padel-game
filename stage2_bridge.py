import sys
import numpy as np
from shapely.geometry import LineString, Point
from racket_lib import (calibrated_outline, sample_spans, outline_polygon,
                        channel_polys, min_curvature_radius, cubic_points,
                        edge_x_at)
import racket_svg as rs

# ---- channel parameter sets, one per iteration -----------------------------
ITERATIONS = {
    1: dict(width=7.0, y_open=246.0, open_dy=2.0, overshoot=3.0,
            c1_in=14.0, c1_y=238.0, c2_x=36.0, c2_y=222.0,
            end_x=18.0, end_y=209.0),
    3: dict(width=8.0, y_open=248.0, overshoot=4.0,
            ctrl=[(38.0, 245.0), (29.0, 241.5), (23.0, 236.0), (18.5, 227.5)]),
    4: dict(width=8.0, y_open=248.0, overshoot=9.0,
            ctrl=[(36.0, 244.0), (27.0, 240.5), (21.5, 234.5), (18.5, 226.5)]),
    5: dict(width=7.5, y_open=249.0, overshoot=9.0,
            ctrl=[(35.0, 246.0), (26.0, 242.5), (21.0, 236.0), (18.25, 227.5)]),
    6: dict(width=7.5, y_open=249.0, overshoot=9.0,
            ctrl=[(34.0, 246.0), (24.0, 243.0), (19.0, 236.5), (18.25, 228.0)]),
    7: dict(width=7.5, y_open=249.0, overshoot=9.0,
            ctrl=[(34.0, 246.0), (24.0, 243.0), (19.0, 236.0), (18.25, 226.0)]),
}

N = int(sys.argv[1]) if len(sys.argv) > 1 else 1
P = ITERATIONS[N]

spans, _ = calibrated_outline()
pts = sample_spans(spans, 80)
outline = outline_polygon(spans)
chR, chL, cl = channel_polys(pts, P)

# ---- verification ----------------------------------------------------------
area_in = chR.intersection(outline).area
muzzle = chR.distance(chL)
axis = LineString([(0, 190), (0, 262)])
half_path = chR.distance(axis)

# mouth corners = where the channel boundary crosses the outline
cross = chR.exterior.intersection(outline.exterior)
corners = [np.array([g.x, g.y]) for g in
           (cross.geoms if cross.geom_type != "Point" else [cross])]
MOUTH_R = 12.0
arm_min = 1e9
feather = []          # outline stretch where solid beside channel is < 9 mm
for y in np.arange(192, 262, 0.5):
    ex = edge_x_at(pts, y)
    p = Point(ex, y)
    d = chR.distance(p)
    near_mouth = any(np.hypot(ex - c[0], y - c[1]) < MOUTH_R for c in corners)
    if d < 9.0:
        feather.append((y, d, near_mouth))
    if not near_mouth:
        arm_min = min(arm_min, d)
print(f"mouth corners: {[tuple(c.round(1)) for c in corners]}")

r_min = min_curvature_radius(np.asarray(cl.coords))

miny_ch = min(y for _, y in chR.exterior.coords)
solid = outline.difference(chR).difference(chL)

print(f"iteration {N}")
print(f"  channel area (per side, inside outline): {area_in:.0f} mm^2 (limit 600)")
print(f"  channel width: {P['width']} mm (spec 6-9)")
print(f"  muzzle min width (between channels)    : {muzzle:.1f} mm (min solid 9)")
print(f"  load path half-width (channel->axis)   : {half_path:.1f} mm (need >=14)")
print(f"  outer arm min width (channel->outline) : {arm_min:.1f} mm (min solid 9)")
print(f"  centreline min curvature radius        : {r_min:.1f} mm (need >=6.5 for r3 inner fillet)")
print(f"  channel lowest point y                 : {miny_ch:.1f} (handle top at 190)")
if feather:
    ys = [f[0] for f in feather]
    print(f"  sub-9mm solid beside channel: y {min(ys):.1f}..{max(ys):.1f} "
          f"({(max(ys)-min(ys)):.1f} mm of edge, mouth wedge)"
          f" all_near_mouth={all(f[2] for f in feather)}")
print(f"  solid is single piece                  : {solid.geom_type == 'Polygon'}")

# erosion connectivity: face<->handle corridor of >=14 mm total width per side
er = solid.buffer(-7.0)
def same_component(g, a, b):
    geoms = [g] if g.geom_type == "Polygon" else list(g.geoms)
    for gg in geoms:
        if gg.contains(Point(a)) and gg.contains(Point(b)):
            return True
    return False
print(f"  14 mm corridor face->handle survives erosion: {same_component(er, (0, 350), (0, 50))}")
er45 = solid.buffer(-4.5)
print(f"  9 mm min-solid global check (erosion -4.5)   : {same_component(er45, (0, 350), (0, 50))}")

# ---- render ----------------------------------------------------------------
svg = rs.build_svg(spans, channels=[chR, chL], dims=True,
                   title=f"iteration {N} - bridge")
rs.write_svg(f"iteration_{N}.svg", svg)
rs.render_png(f"iteration_{N}.svg", f"preview_iter{N}.png")

# zoomed bridge crop for the moose read
zoom = svg.replace(f'viewBox="0 0 {rs.W} {rs.H}"', 'viewBox="75 180 180 130"')
rs.write_svg(f"iteration_{N}_zoom.svg", zoom)
import cairosvg
cairosvg.svg2png(url=f"iteration_{N}_zoom.svg",
                 write_to=f"preview_iter{N}_zoom.png",
                 output_width=900, output_height=650)
print(f"  wrote iteration_{N}.svg, preview_iter{N}.png, preview_iter{N}_zoom.png")
