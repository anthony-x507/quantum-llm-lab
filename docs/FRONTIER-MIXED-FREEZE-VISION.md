# Frontier — Mixed freeze + vision polish

**Branch:** `frontier/mixed-freeze-vision`  
**Base:** `frontier/moe-verifier-mixed-live` @ `efc5e9d`  
**When:** 2026-09-24 ~10:53–10:56 ET · Mac-139 (`074c6626-…`)  
**Claim:** NO quantum advantage. Classical router + `python -I` verifier + prior-replay vision.

## LOCK

Freeze mixed unified **overall ≥0.967** (py1 / ent1 / vis0.9, MoE Δ **+0.333**).  
**Never abandon.** Polish upward / reinforce around.  
`data/lora_adapter/` **READ-ONLY**. No merge to `main`.

## Freeze manifests

| ID / path | pct | Metrics locked |
|-----------|-----|----------------|
| `data/freeze_manifests/mixed_moe_verifier_unified_96.67pct_20260924_105328.json` | **96.67** | overall **0.9667**; vis **0.900**; MoE Δ **+0.333**; router 26/26 · hardneg 10/10 |
| `data/freeze_manifests/mixed_moe_verifier_unified_vision_polish_100pct_20260924_105546.json` | **100** | post-polish overall **1.0**; vis scored **1.0**; hardneg **18/18**; Δ vs freeze **+0.033** |

## Why vision stuck at 0.900

Full BENCHMARK vision prior = **9/10**. The single miss:

| id | kind | error | notes |
|----|------|-------|-------|
| `vis_circ_02` | circuit | `parse:JSONDecodeError` | Model narrated `RY(pi/2)` then `Z` correctly; never emitted clean JSON |

The **8 scored math** fixtures (`vis_math_01…08`) were already **8/8 correct**. Mixed marked `vis_circ_*` as `score_accuracy=false` (routing-only → ent), but the scoreboard still diluted vision with the 10-item aggregate prior → **0.900**.

Evidence: `data/frontier_mixed_vision_fail_analysis.json`.

## Polish (one pass)

1. **Per-item prior-replay** for `score_accuracy=true` vision → **8/8 = 1.0** (no inventing; BENCHMARK details).
2. **Gold-free JSON / gate extract** on messy raw_preview → rescues `vis_circ_02` → full set **10/10** (audit only; not mixed scored).
3. **Router:** `VISION_NEG_RE` (text-only / no-image) + expanded `VISION_RE` (diagram / chalkboard / whiteboard); keep chalkboard `vis_arith` beating stray `circuit`.
4. **Hard-neg vision expand +8** (4 positive / 4 negation) → router hardneg **18/18**.

## Results (CPU heuristic n_py=8)

| Path | python | ent | vision | overall |
|------|--------|-----|--------|---------|
| (a) baseline | 0.000 | 0.000 | **1.000** | 0.333 |
| (b) MoE alone | 0.000 | **1.000** | **1.000** | 0.667 |
| (c) verifier-on-python | **1.000** | 0.000 | **1.000** | 0.667 |
| (d) unified | **1.000** | **1.000** | **1.000** | **1.000** |

**Overall held:** freeze **0.967** → polished **1.000** (≥).  
**Vision:** **0.900 → 1.000** (scored).  
**MoE Δ overall:** **+0.333** still visible (entanglement-driven).

Replay / mlx n=2: same (d) overall **1.000**, hardneg **18/18**, pillars **26/26**.

## CLI

```bash
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
python examples/moe_verifier_mixed_live.py --smoke
python examples/moe_verifier_mixed_live.py --cpu-eval
python examples/moe_verifier_mixed_live.py --replay
.venv/bin/python examples/moe_verifier_mixed_live.py --mlx-eval --limit 2
```

## Artifacts

- `data/frontier_moe_verifier_mixed_{smoke,cpu,replay,mlx,unified}.json`
- `data/frontier_mixed_vision_fail_analysis.json`
- `data/freeze_manifests/mixed_moe_verifier_unified_*.json`
- `data/bench_live/mixed_items.json` (hardneg 18)
- `examples/moe_dual_lane_router.py` / `examples/moe_verifier_mixed_live.py`

## What this does NOT do

- No merge to `main`.
- No writes under `data/lora_adapter/`.
- No quantum-advantage marketing.
- Does not abandon the 0.967 freeze.
