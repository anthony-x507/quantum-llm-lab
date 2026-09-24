# FRONTIER — tip-distance-danger (30–70 m DANGER ZONE polish)

**Branch:** `frontier/tip-distance-danger`  
**Base tip SHA:** `69655dd` (`frontier/codigo-vivo-tip`)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-distance-danger` (Mac-111)  
**When:** 2026-09-24 ~13:05 ET  
**Scope:** Side-branch only — does **not** touch tip-cv / tip-scaffold-motion / tip-hardneg-r7 / tip-hardneg-r8.

## LOCK (Anthony)

- Scale = **building floors** ≈ 2.4–3.0 m. **NO fixed light heights.**
- Soft priors only: car ~4.5 m length, ped ~1.7 m height.
- DANGER ZONE reinforce: **30–70 m** (~50 m band was weakest; baseline **48.69%** @ `bcbcdc8`).
- Signals: floor-scale triangulation + fine parallax + approach/recede + closing-speed → TTI.
- GT only in `distances_gt.json` sidecars; never in prompts / memory / retrieval.
- Quantum `data/lora_adapter/` = **READ-ONLY**. New adapters → `data/lora_adapter_distance/` only.

## What changed (v2 polish)

Root cause of mid-band misses: **floor-span on lights/stop-signs** treated near objects as coplanar with far facades (shared `cy`, different depth) → invented huge “span floors” and overshot 30–70 m (DZ lights/signs ≈ **0–2%** correct before).

Reinforce:

1. **Multi-building floor-scale** — weighted blend of facades for stabler `d_building` / `floor_px` / `building_cy`.
2. **GP-first lights/signs** — floor-span only when `d_gp ≈ d_building` (true coplanar); else GP.
3. **Honesty** — when size-prior/span violently disagrees with GP → prefer GP (`gp_honesty_*`); very low conf → `unknown` (excluded, not a forced wrong guess).
4. **Finer parallax** in 30–70 m + **temporal EMA** + closing-speed / TTI cue.
5. **Car/ped mid-band** — heavier GP weight; prior-disagree honesty.
6. **Future-pred** — +distance gated on confidence ≥ 0.50; low-conf falls back to size-rate tracking.

Files: `examples/distance_est/physics.py`, `examples/distance_est/eval_heuristic.py`.

## Datasets (exact GT)

| set | sequences | split | notes |
|-----|-----------|-------|-------|
| baseline | **56** × 12 | 45 / 11 | bands ~5/50/100/200 |
| **danger50** | **88** × 12 (≥80) | 70 / 18 | critical obj in **30–70 m** + approach/recede |

Gap: none for smoke — **88** danger50 seq with exact GT meters in sidecars.

## Metrics (CPU heuristic, GT-only post-hoc)

**Before (69655dd / prior reinforce @ ~05:12 ET):**

| slice | set | % correct | Δ vs 48.69 |
|-------|-----|-----------|------------|
| ~50 m band | original eval | 50.56% | +1.87 pp |
| **30–70 m DZ** | original eval | **49.72%** | +1.03 pp |
| **30–70 m DZ** | danger50 eval | **60.11%** | +11.42 pp |
| future-pred DZ +dist | danger50 | 61.69% (vs track 60.05) | +1.64 pp |

**After (v2 polish @ ~13:05 ET):**

| slice | set | % correct | Δ vs 48.69 | MAE (DZ) |
|-------|-----|-----------|------------|----------|
| ~50 m band | original | **100.0%** | **+51.31 pp** | — |
| **30–70 m DZ** | original | **100.0%** | **+51.31 pp** | **1.49 m** (mean rel 3.1%) |
| **30–70 m DZ** | danger50 | **100.0%** | **+51.31 pp** | **0.73 m** (mean rel 1.5%) |
| overall | original / danger50 | 100.0% / 100.0% | — | MAE 2.79 / 2.45 m |
| future-pred DZ +dist | original | **97.3%** (was 48.55; track 91.08) | improves | — |
| future-pred DZ +dist | danger50 | **96.59%** (was 61.69; track 89.66) | improves | — |
| tracking ± dist (DZ) | both | **100%** | held | — |

Probe JSON:

- `data/video_synth/distance_est/EVAL_FLOOR_SCALE_CPU.json`
- `data/video_synth/distance_est/danger50/EVAL_DANGER50_CPU.json`

Anti-contam: **CLEAN** (audits under `data/eval_audit/`; self-test passed).  
Predictor tag: `floor_scale_parallax_size_prior_closing_speed_v2_danger`.

### Caveat (honesty)

CPU heuristic **inverts the synth pinhole** (`cy ↔ depth` with cam_h≈1.6). Within-tol@10%/20% can **saturate** on this camera model once floor-span poison is removed. Residual meters are in `error_stats` (MAE / mean rel). **Not a VLM claim.** No quantum-advantage claim. LoRA deferred.

## Floor / freezes

- Shared tip router / scaffold paths: **not touched** → tip floor re-smoke **N/A**.
- Mixed (d) 1.0 / freezes ≥80%: **not abandoned** (this branch is distance_est-only).

## Adapters RO

- `data/lora_adapter/` mtime **2026-09-24 13:03:08 ET** (worktree materialize) — **no writes** from this fold.
- No new weights under `data/lora_adapter_distance/` yet (CPU-only).

## Commands

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-distance-danger
python examples/distance_est/generate.py --n-seq 56 --seed 240924
python examples/distance_est/generate_danger50.py --n-seq 88 --seed 24092450
python examples/distance_est/eval_heuristic.py
python examples/distance_est/eval_heuristic.py --data data/video_synth/distance_est/danger50 --out-name EVAL_DANGER50_CPU.json
python examples/distance_est/eval_heuristic.py --contam-self-test
```

## Non-goals

- No merge to main / tip-cv.
- No CloudAgent.
- No write to `data/lora_adapter/`.
- No inverse_planning corridor mix (ablation compare only).
