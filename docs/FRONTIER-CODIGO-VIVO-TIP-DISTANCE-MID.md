# FRONTIER — tip-distance-mid (5–30 m / 70–100 m outside frozen DZ)

**Branch:** `frontier/tip-distance-mid`  
**Base tip SHA:** `fabef2b` (`frontier/codigo-vivo-tip` @ R10; **avoids** inverse-r2 / tip-cv)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-distance-mid` (Mac-111)  
**When:** 2026-09-24 ~14:00 ET  
**Scope:** Side-branch only — does **not** fold into tip / tip-cv / tip-hardneg-r11 / tip-motion-r4 / tip-inverse-r2 / tip-vision-ground.

## LOCK (Anthony)

- Scale = **building floors** ≈ 2.4–3.0 m. **NO fixed light heights.**
- Soft priors only: car ~4.5 m length, ped ~1.7 m height.
- **DANGER ZONE 30–70 m is FROZEN at 100%** (tip-distance-danger). Do not regress.
- This branch targets **outside DZ**: mid_near **5–30 m** and mid_outer **70–100 m** → ≥80–100%.
- GT only in `distances_gt.json` sidecars; never in prompts / memory / retrieval.
- Quantum `data/lora_adapter/` = **READ-ONLY**. New adapters → `data/lora_adapter_distance/` only.

## What changed (v3 mid polish)

DZ path unchanged when `in_danger_zone`. Outside DZ:

1. **Outer mid (70–100 m)** — GP-heavy triangulation like DZ (weak size/span priors at range); finer parallax on approach/recede → cuts outer MAE.
2. **Near mid (5–30 m)** — stronger soft size priors (objects large/clear); honesty threshold relaxed so priors can win when sharp.
3. **Focused mid dataset** — `generate_mid.py` → 96 seq (48 near / 48 outer), critical objs in target band + approach/recede; buildings non-coplanar for near (stress GP-first).
4. **Eval slices** — `mid_near_5_30m` / `mid_outer_70_100m` reported alongside frozen DZ.

Files: `examples/distance_est/physics.py`, `eval_heuristic.py`, `generate_mid.py`.

## Datasets

| set | sequences | split | notes |
|-----|-----------|-------|-------|
| baseline | 56 × 12 | 45 / 11 | bands ~5/50/100/200 |
| danger50 | 88 × 12 | 70 / 18 | DZ focus (frozen) |
| **mid** | **96** × 12 | 77 / 19 | **5–30 + 70–100** critical |

## Metrics (CPU heuristic, GT-only post-hoc)

Predictor: `floor_scale_parallax_size_prior_closing_speed_v3_mid`

### BEFORE (tip fabef2b physics, mid eval set)

| slice | n | % correct | MAE |
|-------|---|-----------|-----|
| mid_near 5–30 m | 684 | **100.0%** | 0.230 m |
| mid_outer 70–100 m | 374 | **100.0%** | 2.081 m |
| DZ 30–70 m | 55 | **100.0%** | 1.482 m |
| future +dist near | 639 | 94.21% | — |
| future +dist outer | 353 | 96.88% | — |

### AFTER (v3 mid polish)

| slice | set | % correct | MAE | note |
|-------|-----|-----------|-----|------|
| **mid_near 5–30** | mid | **100.0%** | 0.305 m | held ≥80 |
| **mid_outer 70–100** | mid | **100.0%** | **1.624 m** | MAE −0.46 m |
| **DZ 30–70** | mid | **100.0%** | 1.505 m | **held** |
| mid_near | original | **100.0%** | 0.306 m | held |
| mid_outer | original | **100.0%** | **4.662 m** | was 5.359 |
| **DZ 30–70** | original | **100.0%** | 1.489 m | **held 100%** |
| **DZ 30–70** | danger50 | **100.0%** | 0.726 m | **held 100%** |
| future +dist near | mid | **94.68%** | — | +0.47 pp |
| future +dist outer | mid | **96.88%** | — | held |
| future +dist DZ | original | **97.3%** | — | held |
| tracking ± dist (DZ) | all | **100%** | — | held |

Probe JSON:

- `data/video_synth/distance_est/mid/EVAL_MID_CPU.json`
- `data/video_synth/distance_est/mid/EVAL_MID_BEFORE.json`
- `data/video_synth/distance_est/mid/EVAL_MID_AFTER.json`
- `data/video_synth/distance_est/EVAL_FLOOR_SCALE_CPU.json`
- `data/video_synth/distance_est/danger50/EVAL_DANGER50_CPU.json`

Anti-contam: **CLEAN**.  
Caveat: synth pinhole invert can saturate tol@10/20% — MAE shows residual. **Not a VLM claim.** No quantum-advantage claim.

## Floor / freezes

- Shared tip router / scaffold paths: **not touched** → tip mixed floor re-smoke **N/A** (distance_est-only).
- Mixed (d) 1.0 / freezes ≥80%: **not abandoned**.
- **Freeze:** `codigo_vivo_tip_distance_mid_100pct` — mid_near & mid_outer ≥80% (actually 100%) with DZ held 100%.

## Adapters RO

- `data/lora_adapter/` mtime unchanged from worktree materialize — **no writes**.
- No new weights under `data/lora_adapter_distance/` (CPU-only).

## Commands

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-distance-mid
python examples/distance_est/generate_mid.py --n-seq 96 --seed 24092470
python examples/distance_est/eval_heuristic.py --data data/video_synth/distance_est/mid --out-name EVAL_MID_CPU.json
python examples/distance_est/eval_heuristic.py  # original; DZ must stay 100%
python examples/distance_est/eval_heuristic.py --data data/video_synth/distance_est/danger50 --out-name EVAL_DANGER50_CPU.json
python examples/distance_est/eval_heuristic.py --contam-self-test
```

## Non-goals

- No merge to main / tip / tip-cv.
- No CloudAgent.
- No write to `data/lora_adapter/`.
- No fold of inverse-r2 / hardneg-r11 / motion-r4 / vision-ground.
