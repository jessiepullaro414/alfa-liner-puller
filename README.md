# alfa-liner-puller

Wet-liner removal tools for Alfa Romeo engines: a parametric generator, plus ready-to-use CAD files (STEP and STL) for each engine size.

## Buy one

Ready-made tools are for sale at **[jessiescars.com](https://www.jessiescars.com)**. Currently listed: the 2.0 L "Nord" tool, the [Piston Liner Removal Tool](https://www.jessiescars.com/product/piston-liner-removal-tool). Its product page includes step-by-step instructions for using it.

## What's here

| File prefix | Engine | Bore | Status |
|---|---|---|---|
| `puller_2000_check` | 2000 cc Nord | 84.0 mm | Reference: reproduces the real 2.0 L tool this design comes from (register 88.75 mm) |
| `puller_1300_BLANK`, `puller_1600_BLANK` | 1300 / 1600 cc | 78.0 mm | Starting blank, not verified |
| `puller_1750_BLANK` | 1750 cc | 80.0 mm | Starting blank, not verified |
| `puller_TS17_8V_BLANK` | 1.7 Twin Spark 8V | 83.4 mm | Starting blank, not verified |
| `puller_TS18_8V_BLANK`, `puller_TS20_8V_BLANK` | 1.8 / 2.0 Twin Spark 8V | 84.0 mm | Starting blank, not verified |

Each comes as `.step` (for CAD and machining) and `.stl` (for printing), plus a `_size` variant with the engine size etched 0.6 mm deep into the top of the pilot boss. The etch is only a shop-identification mark, not a functional dimension.

### About the "BLANK" files

Only the 2000 cc tool is checked against a real tool and a measured liner. For the other sizes the liner register diameter is not published anywhere public (factory manuals only give the bore), so the blanks use the same relationship measured on the 2.0 L (register = bore + 4.75 mm) as a **conservative starting point, oversized on purpose** so material can be ground away to fit, never undersized. The 1300 and 1600 bores come from the factory tolerance table; the 1750 and Twin Spark bores are well-corroborated figures rather than from an official table.

The 8V Twin Spark engines are a reworked evolution of the Nord block, with a different casting, so their register is not assumed to match the Nord's even where the bore does.

**Do not machine a BLANK to final size without checking its register diameter against an actual liner first.**

## Regenerate or adapt

```
pip install cadquery
python make_liner_puller.py
```

This rewrites every file above into the current directory. To make another size, call `make_puller(bore_id, register_od, name, label)` from the bottom of the script.

The geometry is fixed except for those two diameters: a pilot boss (5 mm tall, bore minus 0.2 mm) enters the liner's bore to centre the tool, and a base (10 mm tall, register minus 0.75 mm) rides in the block's liner register and pushes on the underside of the liner. Both share an obround footprint (58 mm across the short axis) so the tool can be angled past crankcase webbing, and a 21 mm through-hole takes the puller rod.

## License

See [LICENSE](LICENSE).
