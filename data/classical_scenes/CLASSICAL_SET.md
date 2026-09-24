# CLASSICAL_SET

Balanced synthetic classical motion scenes for image→Python→numeric eval.

N = **220** (seed=240924).

## Subdomains
- `angled_projectile`: 27
- `ballistic`: 28
- `baseball`: 28
- `drag_projectile`: 27
- `elastic_collision`: 27
- `golf`: 28
- `inelastic_collision`: 27
- `soccer`: 28

## Eval protocol
1. Model sees PNG + anti-leak user prompt (no gold numbers).
2. Model emits executable Python.
3. Runner execs Python; parses printed `{range_m, max_height_m, impact_speed_m_s}`.
4. Pass if all three within `meta.tolerance`.

## Sample scenes (first 8)
- `cscene_0000` (drag_projectile): R=24.625 H=8.778 V=11.401 verified=True
- `cscene_0001` (golf): R=3776.719 H=1217253.618 V=224817.863 verified=True
- `cscene_0002` (baseball): R=126.998 H=18.929 V=36.282 verified=True
- `cscene_0003` (elastic_collision): R=2.836 H=0.000 V=1.097 verified=True
- `cscene_0004` (angled_projectile): R=87.209 H=19.529 V=29.978 verified=True
- `cscene_0005` (soccer): R=23.210 H=4.782 V=15.221 verified=True
- `cscene_0006` (golf): R=3671.999 H=4987621395.251 V=1551296603.359 verified=True
- `cscene_0007` (angled_projectile): R=16.223 H=6.199 V=13.661 verified=True
