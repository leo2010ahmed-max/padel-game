import numpy as np
from racket_lib import (calibrated_outline, sample_spans, outline_polygon,
                        HANDLE_LEN, HEAD_LEN, TOTAL_LEN)
import racket_svg as rs

spans, cal = calibrated_outline()
pts = sample_spans(spans, 80)
poly = outline_polygon(spans)

ymin, ymax = pts[:, 1].min(), pts[:, 1].max()
xmax = pts[:, 0].max()
y_at_widest = float(pts[np.argmax(pts[:, 0]), 1])
frac = (y_at_widest - HANDLE_LEN) / HEAD_LEN

# handle width along its length
hw = []
for y in np.arange(5, 190, 5):
    m = pts[(np.abs(pts[:, 1] - y) < 2.5) & (pts[:, 0] > 0)]
    if len(m):
        hw.append((y, 2 * m[:, 0].max()))
hw_max = max(w for _, w in hw)
hw_throat = [w for y, w in hw if y > 180][-1]

# curvature sanity along the whole outline (kink check)
d1 = np.gradient(pts[:-1], axis=0)
ang = np.unwrap(np.arctan2(d1[:, 1], d1[:, 0]))
max_turn = np.abs(np.diff(ang)).max()

print(f"calibration: dy_bot={cal[0]:.3f} dy_top={cal[1]:.3f} sx={cal[2]:.5f}")
print(f"total length  : {ymax - ymin:.3f} mm (target 453, limit 455)")
print(f"head width    : {2 * xmax:.3f} mm (target 257, limit 260)")
print(f"widest point  : y={y_at_widest:.1f} -> {100 * frac:.1f} % of head length (spec 60-62)")
print(f"handle width  : max {hw_max:.2f} mm, at throat {hw_throat:.2f} (limit 50)")
print(f"max per-sample turn angle: {np.degrees(max_turn):.3f} deg (kink check)")
print(f"bezier spans  : {len(spans)}")
print(f"outline area  : {poly.area:.0f} mm^2")

svg = rs.build_svg(spans, dims=True, title="stage 1 - outline")
rs.write_svg("iteration_stage1_outline.svg", svg)
rs.render_png("iteration_stage1_outline.svg", "preview_stage1.png")
print("wrote iteration_stage1_outline.svg / preview_stage1.png")
