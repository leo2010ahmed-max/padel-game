"""SVG / PNG export for the moose-teardrop racket. True scale: 1 SVG unit = 1 mm."""

import numpy as np

W, H = 330.0, 474.0          # sheet size mm
CX = 165.0                   # centreline x on sheet
YT = 464.0                   # design y=0 maps to sheet y=YT (y flipped)

NAVY = "#0B1F3A"
RED = "#C8102E"


def tx(p):
    return (CX + p[0], YT - p[1])


def fmt(v):
    return f"{v:.3f}".rstrip("0").rstrip(".")


def bezier_path(spans):
    d = [f"M {fmt(tx(spans[0][0])[0])} {fmt(tx(spans[0][0])[1])}"]
    for b0, b1, b2, b3 in spans:
        p1, p2, p3 = tx(b1), tx(b2), tx(b3)
        d.append(f"C {fmt(p1[0])} {fmt(p1[1])} {fmt(p2[0])} {fmt(p2[1])} "
                 f"{fmt(p3[0])} {fmt(p3[1])}")
    d.append("Z")
    return " ".join(d)


def poly_path(poly):
    pts = [tx(p) for p in np.asarray(poly.exterior.coords)]
    d = [f"M {fmt(pts[0][0])} {fmt(pts[0][1])}"]
    d += [f"L {fmt(x)} {fmt(y)}" for x, y in pts[1:]]
    d.append("Z")
    return " ".join(d)


def dim_v(x, y1, y2, label, side=1):
    """Vertical dimension line with ticks at sheet position x (design coords in)."""
    (sx, sy1), (_, sy2) = tx((x, y1)), tx((x, y2))
    t = 2.5
    txt_y = (sy1 + sy2) / 2
    return (f'<line x1="{fmt(sx)}" y1="{fmt(sy1)}" x2="{fmt(sx)}" y2="{fmt(sy2)}"/>'
            f'<line x1="{fmt(sx - t)}" y1="{fmt(sy1)}" x2="{fmt(sx + t)}" y2="{fmt(sy1)}"/>'
            f'<line x1="{fmt(sx - t)}" y1="{fmt(sy2)}" x2="{fmt(sx + t)}" y2="{fmt(sy2)}"/>'
            f'<text x="{fmt(sx + 2 * side)}" y="{fmt(txt_y)}" '
            f'transform="rotate(-90 {fmt(sx + 2 * side)} {fmt(txt_y)})" '
            f'text-anchor="middle">{label}</text>')


def dim_h(y, x1, x2, label, dy_txt=-1.5):
    (sx1, sy), (sx2, _) = tx((x1, y)), tx((x2, y))
    t = 2.5
    return (f'<line x1="{fmt(sx1)}" y1="{fmt(sy)}" x2="{fmt(sx2)}" y2="{fmt(sy)}"/>'
            f'<line x1="{fmt(sx1)}" y1="{fmt(sy - t)}" x2="{fmt(sx1)}" y2="{fmt(sy + t)}"/>'
            f'<line x1="{fmt(sx2)}" y1="{fmt(sy - t)}" x2="{fmt(sx2)}" y2="{fmt(sy + t)}"/>'
            f'<text x="{fmt((sx1 + sx2) / 2)}" y="{fmt(sy + dy_txt)}" '
            f'text-anchor="middle">{label}</text>')


def note(x, y, label, anchor="start"):
    sx, sy = tx((x, y))
    return f'<text x="{fmt(sx)}" y="{fmt(sy)}" text-anchor="{anchor}">{label}</text>'


def build_svg(spans, channels=None, holes=None, dims=True, extra_notes=(),
              title="moose teardrop padel profile"):
    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" '
                 f'height="{H}mm" viewBox="0 0 {W} {H}">')
    parts.append(f'<title>{title}</title>')
    parts.append(f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>')

    parts.append(f'<g id="OUTLINE" fill="{NAVY}" stroke="{NAVY}" stroke-width="0.4">')
    parts.append(f'<path d="{bezier_path(spans)}"/>')
    parts.append('</g>')

    if channels:
        parts.append(f'<g id="BRIDGE_CUTOUTS" fill="{RED}" stroke="none">')
        for ch in channels:
            parts.append(f'<path d="{poly_path(ch)}"/>')
        parts.append('</g>')

    if holes:
        parts.append(f'<g id="HOLES" fill="#FFFFFF" stroke="{NAVY}" stroke-width="0.5">')
        for (x, y), d in holes:
            sx, sy = tx((x, y))
            parts.append(f'<circle cx="{fmt(sx)}" cy="{fmt(sy)}" r="{fmt(d / 2)}"/>')
        parts.append('</g>')

    # centreline
    (clx, cly1), (_, cly2) = tx((0, -6)), tx((0, 459))
    parts.append(f'<g id="CENTRELINE" stroke="#8A94A6" stroke-width="0.3" '
                 f'stroke-dasharray="8 3 1.5 3" fill="none">'
                 f'<line x1="{fmt(clx)}" y1="{fmt(cly1)}" x2="{fmt(clx)}" y2="{fmt(cly2)}"/>'
                 f'</g>')

    if dims:
        parts.append('<g id="DIMENSIONS" stroke="#333333" stroke-width="0.25" '
                     'fill="#333333" font-family="Helvetica,Arial,sans-serif" '
                     'font-size="4.2">')
        parts.append(dim_v(-152, 0, 453, "453 (total, FIP max 455)"))
        parts.append(dim_v(-140, 0, 190, "190 handle (max 200)"))
        parts.append(dim_v(-140, 190, 260, "70 bridge"))
        parts.append(dim_v(-140, 260, 453, "193 face"))
        parts.append(dim_h(457, -128.5, 128.5, "257 head width (FIP max 260)", dy_txt=-1.8))
        parts.append(dim_h(-4, -22.4, 22.4, "44.8 handle at throat (max 50)", dy_txt=5.2))
        if holes:
            from racket_lib import SWEET_Y, SWEET_R
            sx, sy = tx((0, SWEET_Y))
            parts.append(f'<circle cx="{fmt(sx)}" cy="{fmt(sy)}" r="{SWEET_R}" '
                         f'fill="none" stroke-dasharray="4 2"/>')
            parts.append(note(85, 272, "sweet-spot core: pitch 16 inside dashed"))
            parts.append(note(85, 266.5, "R42 at 55% head height; elsewhere"))
            parts.append(note(85, 261, "pitch 17.5; all holes O11 cylindrical"))
        if channels:
            parts.append(note(70, 205, "2x bridge channel, 7.5 wide,"))
            parts.append(note(70, 199.5, "open to throat edge, r3.75 ends"))
        for n in extra_notes:
            parts.append(n)
        parts.append('</g>')

    parts.append('</svg>')
    return "\n".join(parts)


def write_svg(path, svg):
    with open(path, "w") as f:
        f.write(svg)


def render_png(svg_path, png_path, scale=2.0):
    import cairosvg
    cairosvg.svg2png(url=svg_path, write_to=png_path,
                     output_width=int(W * scale), output_height=int(H * scale))
