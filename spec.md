# Moose Teardrop — Padel Racket 2D Profile Specification

**Files:** `moose_teardrop_profile.svg` (1:1, mm), `moose_teardrop_profile.dxf`
(closed polylines, mm, layers `OUTLINE / BRIDGE_CUTOUTS / HOLES / HANDLE /
ANNOTATIONS`), `preview.png`, bridge design history `iteration_1.svg` …
`iteration_7.svg`.

**Coordinate system:** millimetres, origin at the handle butt on the
centreline, +y toward the crown. All values below are *measured from the
generated geometry* (shapely, sampled at ≤0.1 mm), not nominal intent.

---

## 1. Dimensions

### Envelope

| Dimension | Value | FIP 2026 hard limit | Status |
|---|---|---|---|
| Total length (head + handle) | **453.00** | ≤ 455 | design target, 2.0 margin |
| Head max width | **257.00** | ≤ 260 | design target, 3.0 margin |
| Widest point (from throat, % of head length) | **349.2 mm → 60.5 %** | none (design rule 60–62 %) | ✓ |
| Head length (throat y=190 → crown) | **263.00** | — | 453 − 190 |
| Handle length (butt → throat) | **190.00** | ≤ 200 | design target |
| Handle width at throat | **44.89** (max anywhere on handle) | ≤ 50 | target 45, tapers to ≈41 at butt |
| Bridge height | **70** (y 190–260) | — | design choice |
| Bridge width at base (y=260) | **124.9** | — | design choice (~120 spec) |
| Thickness | **38** (note only, not modelled in 2D) | ≤ 38 | flat profile |

### Outline construction

Closed **uniform periodic cubic B-spline** (C2 ⇒ curvature-continuous, G2)
over a 36-point mirror-symmetric control polygon, converted **exactly** to 36
cubic Bézier spans (the SVG `OUTLINE` path is those Béziers verbatim; the DXF
outline is the same curve sampled at 60 points/span, chord error < 0.01 mm).
The crown is a continuous curve crossing the centreline with horizontal
tangent — no apex, no kinks anywhere (max turn between successive 0.35 mm
samples: 1.2°, consistent with smooth curvature). Control-point extents are
auto-calibrated so length, width and the two symmetry-line tangencies land on
target to < 0.001 mm.

### Bridge / moose channels

| Property | Value | Rule | Status |
|---|---|---|---|
| Channel width (constant, both) | **7.5** | 6–9 | ✓ |
| Cutout area per side (inside outline) | **347.8 mm²** | ≤ 600 | ✓ |
| Total cutout area (both sides) | **695.7 mm²** | — | |
| Min inside fillet radius | **3.75** (round end caps / offset) | ≥ 3 | ✓ |
| Min centreline curvature radius minus half-width | **8.6** | ≥ 3 | ✓ |
| Muzzle (solid between channels), min | **29.0** | ≥ 9 | ✓ |
| Load path, each side of centreline, min | **14.5** | ≥ 14 | ✓ |
| Outer arm (channel → outline), min outside mouth zone | **10.0** | ≥ 9 | ✓ |
| Mouth wedge: sub-9 mm solid confined within | **10.8 mm of the mouth corners** | see §4 | disclosed |
| Channel lowest point | y = 222.3 | stays clear of handle (y=190) | ✓ |
| Channel opening | on the outer throat edge, each side, y ≈ 241–252 | required open to edge | ✓ |

Channel construction: clamped C2 cubic B-spline centreline entering from
outside the outline along the local edge normal (so the slot genuinely
breaches the edge), sweeping inward nearly horizontally, then hooking
downward to a rounded end at (±18.25, 226); offset ±3.75 mm with round caps
and joins.

### Face holes

| Property | Value | Rule | Status |
|---|---|---|---|
| Hole count | **114** | — | |
| Diameter | **11.0, cylindrical** | 9–13 central zone | ✓ |
| Edge-zone (≤40 mm) large-hole allowance | **not used** | optional | per brief |
| Grid | hexagonal, pitch **17.5**; **16.0** inside R42 of sweet spot (0, 334.65 = 55 % head height) | 17–18 / 16 | ✓ |
| Holes in sweet-spot core | **19** | — | |
| Min web between holes | **5.00** | — (sanity ≥ 4) | ✓ |
| Min hole edge → outline | **11.39** | ≥ 10 (bumper band) | ✓ |
| Min hole edge → channel | **19.74** | ≥ 9 | ✓ |
| No hole cut by outline / in perimeter band | verified (centre must sit in outline eroded by 15.5) | required | ✓ |
| Mirror symmetry of pattern | verified exact | — | ✓ |
| Face area (outline region above y=260) | **39 410 mm²** | — | |
| Area removed by holes | **10 834 mm² = 27.5 % of face** | — | |

---

## 2. Balance estimate

**Assumptions (stated, all uniform-slab):**

- The blank is treated as a uniform 38 mm-thick slab of constant *effective*
  density (EVA core ≈ 0.10–0.14 g/cm³ + two ~1 mm carbon skins ≈ 1.5 g/cm³ +
  frame tube smeared over the area). Under this assumption the balance point
  is the **area centroid** and is independent of the density value.
- Effective density taken as **0.23 g/cm³**, chosen so the blank mass lands in
  the typical range: net area 41 249 mm² × 38 mm × 0.23 → **≈ 361 g**
  (before grip, bumper, cap ≈ +25–40 g, which pull the balance handle-ward).
- Not modelled: denser frame ring at the perimeter (would push balance
  head-ward), grip stack, drilled-hole wall skins.

| Quantity | Value |
|---|---|
| Balance point (with bridge cutouts + holes) | **290.8 mm from butt** (64.2 % of total length) |
| Balance without the bridge cutouts | 290.0 mm |
| **Shift caused by the moose channels** | **+0.85 mm head-ward** |

The channels remove 696 mm² at y ≈ 226–250 (below the centroid), so they move
the balance *up*, not down — a small head-heavier bias, ~0.9 mm under the
uniform-slab assumption.

---

## 3. Hard FIP limits vs design choices

**Hard limits (FIP Rules of Padel, 2026 revision — must not be exceeded):**
total length ≤ 455; head width ≤ 260; handle ≤ 200 long / ≤ 50 wide;
thickness ≤ 38; face holes cylindrical 9–13 mm in the central zone (up to
20 mm and non-circular only within 40 mm of the edge).

**Design choices (ours, changeable):** 453/257/190/45 targets and their
margins; teardrop with widest point at 60.5 %; bridge 70 × 125; 10 mm no-hole
perimeter band (bumper channel — engineering reserve, not an FIP rule);
Ø11 holes at 17.5/16 hex pitch; sweet-spot densification radius R42; channel
width 7.5 and the whole moose geometry; 9 mm min-solid, 14 mm load-path and
r3 fillet rules (internal structural policy).

---

## 4. Where the moose lost to the structure (every compromise)

1. **The antlers stop high.** The channels end at y ≈ 222–226 instead of
   sweeping down beside the handle. Below y ≈ 224 the throat is too narrow to
   hold 14 mm load path + 7.5 mm channel + 9 mm outer arm on each side, so the
   antler inner edges are shorter and higher than a literal moose would have.
2. **The muzzle is stocky.** A moose muzzle would taper; ours is a constant
   ≥ 29 mm column because each half must keep the 14 mm load path. The face
   reads wide-jawed rather than long-nosed.
3. **Channel width 7.5, not 9.** A 9 mm channel (the spec maximum) fits the
   area budget but pinches the outer arm below 9 mm in the throat funnel;
   7.5 mm keeps the arm at 10.0 mm minimum.
4. **No tines, no palm notches.** Any secondary notch in the palms would
   create sub-9 mm solids; the antlers are smooth single sweeps.
5. **Mouth wedge (structure lost a little too, disclosed):** an edge-open
   channel necessarily tapers the solid to zero at its mouth corners. Solid
   < 9 mm exists only within **10.8 mm** of the mouth corners (verified
   numerically); everywhere else ≥ 9 mm holds. Mitigation: CAM note to break
   both mouth corners with **r ≥ 3 mm** fillets (also satisfies the internal-
   corner fillet rule at the two concave mouth corners); the 10 mm bumper
   perimeter band is accepted as breached exactly at the two channel mouths —
   the bumper must be interrupted or bridged there (supplier question below).

The moose survives as: two red J-hook channels = inner edges of the antlers,
the outer bridge flares = antler palms, the 29 mm centre column = the long
face/muzzle. No eyes, no detailing; second-look recognition only.

---

## 5. Compliance checklist

- [x] Total length 453.00 ≤ 455 (measured)
- [x] Head width 257.00 ≤ 260 (measured)
- [x] Handle 190.00 ≤ 200 long; 44.89 ≤ 50 wide (measured max on handle)
- [x] Thickness 38 noted, not modelled
- [x] Widest point 60.5 % ∈ [60, 62] of head length from throat
- [x] Crown continuous curve, no apex; outline G2 (C2 B-spline by construction)
- [x] Outline mirror-symmetric cubic Béziers (36 spans, exact conversion)
- [x] All 114 holes Ø11 cylindrical ∈ [9, 13]; edge-zone allowance unused
- [x] Hex pitch 17.5 ∈ [17, 18]; sweet-spot core pitch 16 at 55 % head height
- [x] No hole cut by outline; hole edges ≥ 11.39 mm from outline (≥ 10 required)
- [x] Channels 7.5 mm ∈ [6, 9] wide; open to outer throat edge; run inward + downward
- [x] Cutout area 347.8 mm²/side ≤ 600
- [x] Inside radii ≥ 3.75 ≥ 3
- [x] Min solid ≥ 9 everywhere except ≤ 10.8 mm mouth wedge (r3 corner break at CAM)
- [x] Two load paths ≥ 14.5 ≥ 14 each side, full length (erosion-verified: face
      and handle remain connected after 7 mm erosion of the solid)
- [x] DXF: closed polylines only, one layer per feature, mm units
- [x] Colours: outline #0B1F3A, cutouts #C8102E, holes #FFFFFF/#0B1F3A stroke; no graphics

---

## 6. Open questions for the tooling supplier

1. **Draft angle** on the Ø11 hole walls and the channel walls — we assume
   straight (cylindrical per FIP). If ≥ 0.5° draft is needed for demoulding,
   confirm the holes stay ≥ 9 mm at the narrowest section and whether draft
   should be split about the mid-plane.
2. **Parting line**: mid-thickness assumed. Confirm location, and mismatch
   tolerance at the channel mouths where the parting line crosses the open
   edge.
3. **Core insert for the bridge channels**: machined-in after moulding, or
   steel core insert in-mould? If in-mould, minimum insert cross-section is
   7.5 × 38 mm with r3.75 corners — confirm feasibility and ejection.
4. **Bumper interface at the channel mouths**: the 10 mm perimeter band is
   interrupted at the two openings. Does the bumper strip terminate at each
   mouth, or bridge across (and if so, what retention feature is needed)?
5. **Mouth corner break**: r3 minimum specified — larger preferred? Confirm
   the fillet can be applied on both faces consistently.
6. **Skin layup around the channels**: do the carbon skins wrap into the
   channel walls (preferred for the exposed edges) and what minimum wrap
   radius does that impose vs our 3.75 mm?
7. **Hole pattern**: drilled post-moulding or moulded-in pins? 114 × Ø11 at
   16–17.5 mm pitch — confirm pin density is acceptable for fill/venting.

---

## 7. Reproduction

All geometry is generated by `stage4_final.py` (with `racket_lib.py`,
`racket_svg.py`); `stage1_outline.py`–`stage3_holes.py` reproduce the
intermediate stages, `stage2_bridge.py N` regenerates bridge iteration N.
Measured values above are printed by the scripts and stored in `metrics.json`.
