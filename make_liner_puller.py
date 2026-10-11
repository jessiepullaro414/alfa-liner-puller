"""
Parametric generator for Alfa Romeo "Nord" wet-liner removal tool,
reverse-engineered from the user's real rev1.step/rev1.stl (2000cc / 84mm bore version).

Geometry rule (derived from the verified 2000cc tool + a real caliper-measured
2000cc liner from an alfabb.com forum post):
  - Pilot boss (top, enters the liner's bore from below to center the tool):
        diameter = bore_id - PILOT_CLEARANCE   (84 - 0.2 = 83.8, matches drawing exactly)
        height   = PILOT_HEIGHT
  - Base / catch shoulder (bottom, rides in the block's liner-register bore and
    pushes on the underside of the liner):
        diameter = register_od - BASE_CLEARANCE (88.75 - 0.75 = 88.0, matches drawing)
        height   = BASE_HEIGHT
  - Both boss and base share a stadium/obround footprint (long axis = outer
    diameter, short axis = STADIUM_WIDTH) so the tool can be angled past
    crankcase webbing.
  - A through center hole (CENTER_HOLE) takes the slide-hammer / puller rod.

Only bore_id and register_od are engine-specific unknowns; the rest are
carried over unchanged from the real, measured 2000cc tool.
"""
import cadquery as cq

PILOT_CLEARANCE = 0.2     # mm under bore ID
BASE_CLEARANCE = 0.75     # mm under liner register OD
PILOT_HEIGHT = 5.0        # mm
BASE_HEIGHT = 10.0        # mm
CENTER_HOLE = 21.0        # mm through hole
STADIUM_WIDTH = 58.0      # mm short-axis width of the obround footprint


def stadium_wire(length, width):
    """2D obround (stadium) profile: full-round ends of diameter `length`,
    flats spaced `width` apart, centered on the origin."""
    r = length / 2.0
    half_w = width / 2.0
    dx = r - 0.0  # arc centers sit on the long axis; will offset below
    # Arc centers offset so the two end caps (radius r_end) meet the flats.
    # We build it directly with cadquery's slot helper instead (simpler/robust).
    return None


def make_puller(bore_id, register_od, name, label):
    pilot_d = round(bore_id - PILOT_CLEARANCE, 3)
    base_d = round(register_od - BASE_CLEARANCE, 3)

    # The real tool is NOT a stadium/obround. It's a plain round disc (like a
    # bolt head) with two parallel flats ground onto it, centered on the same
    # axis as the through-hole. The flats run the FULL height uninterrupted
    # (no step there at all); only the round circumference steps down in
    # diameter between the base and pilot tiers. Verified against rev1.step
    # face-by-face: both cylinder faces (r=44 and r=41.9) share axis (0,0,0),
    # and both flat PLANE faces span the full z=0..15 with no break.
    def flatted_disc(diameter, flat_width, height, z_offset=0.0):
        circle = cq.Workplane("XY").circle(diameter / 2.0).extrude(height)
        clip = cq.Workplane("XY").rect(diameter * 2, flat_width).extrude(height)
        disc = circle.intersect(clip)
        return disc.translate((0, 0, z_offset))

    base = flatted_disc(base_d, STADIUM_WIDTH, BASE_HEIGHT, 0.0)
    pilot = flatted_disc(pilot_d, STADIUM_WIDTH, PILOT_HEIGHT, BASE_HEIGHT)
    total_h = BASE_HEIGHT + PILOT_HEIGHT
    bore = (
        cq.Workplane("XY")
        .circle(CENTER_HOLE / 2.0)
        .extrude(total_h)
    )
    solid = base.union(pilot).cut(bore)

    solid = solid.val()
    bb = solid.BoundingBox()
    vol = solid.Volume()
    print(f"{name}: pilot Ø{pilot_d} x {PILOT_HEIGHT}mm, base Ø{base_d} x {BASE_HEIGHT}mm, "
          f"bbox=({bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f}), "
          f"mass@7850kg/m3={vol*7850e-9*1000:.1f} g")

    cq.exporters.export(solid, f"{name}.step")
    cq.exporters.export(solid, f"{name}.stl")

    # Second file: same part with the engine size etched into the pilot-boss
    # top face (0.6mm deep), offset above the center hole so it doesn't cross
    # it. Purely a shop-identification mark - not a functional dimension.
    label_wp = (
        cq.Workplane(obj=solid)
        .faces(">Z")
        .workplane()
        .center(0, 15)
        .text(label, 9, -0.6, combine="cut", halign="center", valign="center")
    )
    labeled_solid = label_wp.val()
    cq.exporters.export(labeled_solid, f"{name}_size.step")
    cq.exporters.export(labeled_solid, f"{name}_size.stl")

    return solid


if __name__ == "__main__":
    # Verified reference case: reproduce the real 2000cc tool exactly.
    make_puller(bore_id=84.0, register_od=88.75, name="puller_2000_check", label="2000")

    # 1300 / 1600 / 1750: the liner register OD is NOT documented anywhere
    # public (confirmed by extensive research - factory manuals only cover
    # bore ID, and community builders hand-fit this dimension off the real
    # liner rather than working from a spec). These use the same
    # register_od = bore_id + 4.75mm relationship measured on the real 2000
    # liner (88.75 - 84 = 4.75) as a CONSERVATIVE STARTING BLANK - oversized
    # on purpose so material can be ground away to match the real liner,
    # never undersized. Bore IDs are factory-confirmed (1300/1600 official
    # tolerance table, 1750 well-corroborated at 80mm).
    # DO NOT machine to final size without verifying register OD against an
    # actual liner first.
    make_puller(bore_id=78.0, register_od=78.0 + 4.75, name="puller_1300_BLANK", label="1300")
    make_puller(bore_id=78.0, register_od=78.0 + 4.75, name="puller_1600_BLANK", label="1600")
    make_puller(bore_id=80.0, register_od=80.0 + 4.75, name="puller_1750_BLANK", label="1750")

    # 8V Twin Spark (Alfa 75 / 155 1.7-2.0 8V, 164): a direct evolution of the
    # Nord block - aluminum, wet liners, same crank interface - but the
    # casting itself was reworked (extra oil galleries for the cam bearing
    # caps, different head), so the liner register is NOT assumed identical
    # to the old Nord's even where the bore happens to match. Same
    # conservative-blank treatment as 1300/1600/1750: bore-based pilot is
    # solid, catch diameter is an oversized starting point to be ground to
    # fit a real liner, not a verified final dimension.
    # Bores: 1.7 TS = 83.4mm, 1.8 TS = 84mm, 2.0 TS = 84mm (155-spec figures;
    # 1.8 and 2.0 share the same bore, so their blanks are identical - only
    # the label differs, same situation as 1300/1600 above).
    make_puller(bore_id=83.4, register_od=83.4 + 4.75, name="puller_TS17_8V_BLANK", label="TS17")
    make_puller(bore_id=84.0, register_od=84.0 + 4.75, name="puller_TS18_8V_BLANK", label="TS18")
    make_puller(bore_id=84.0, register_od=84.0 + 4.75, name="puller_TS20_8V_BLANK", label="TS20")
