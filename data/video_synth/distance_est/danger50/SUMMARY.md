# DANGER ZONE (~50 m) focused set SUMMARY

- **Danger zone:** 30–70 m
- sequences: **88** × 12 frames (all with ≥1 critical @ t0)
- split: train 70 / eval 18
- priority danger-zone observations: **4526**
- approach/recede/stable: {'approach': 3972, 'recede': 3744, 'stable': 3888}

## Eval (improved estimator)

| metric | value |
|--------|-------|
| 30–70 m % correct | **60.11%** |
| Δ vs baseline 48.69% | **+11.42 pp** |
| ~50 m band % | 62.15% (+13.46 pp) |
| overall | 73.54% |
| future-pred danger tracking-only | 60.05% |
| future-pred danger +distance | 61.69% |
| anti-contam | **CLEAN** (`data/eval_audit/danger50_20260924_051252.jsonl`) |

Soft priors (eval): car ~4.5 m, ped ~1.7 m. Lights: floor-span / 3–5 m vary. Baseline commit `bcbcdc8`.
