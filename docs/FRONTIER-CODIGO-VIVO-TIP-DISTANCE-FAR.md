# FRONTIER — tip-distance-far (~100–200 m far-band polish)

**Branch:** `frontier/tip-distance-far`  
**Base tip SHA:** `f70faa1` (`frontier/codigo-vivo-tip` @ motion-r4; **side-only**)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-distance-far` (Mac-111)  
**When:** 2026-09-24 ~14:07 ET  
**Scope:** Side-branch only — does **not** fold into tip / tip-cv / tip-distance-mid / tip-hardneg-r11 / tip-hardneg-r12 / tip-tti / tip-motion-r4 / tip-inverse-r3.

## LOCK (Anthony)

- Scale = **building floors** ≈ 2.4–3.0 m. **NO fixed light heights.**
- Soft priors only: car ~4.5 m length, ped ~1.7 m height.
- **DANGER ZONE 30–70 m is FROZEN at 100%** (tip-distance-danger). Do not regress.
- **Mid bands 5–30 / 70–100 held** (tip-distance-mid side floor; not folded here).
- This branch targets **far ~100–200 m** (far_near 100–150 / far_outer 150–200) → MAE tighten; % already saturated @20% tol.
- GT only in `distances_gt.json` sidecars; never in prompts / memory / retrieval.
- Quantum `data/lora_adapter/` = **READ-ONLY**. New adapters → `data/lora_adapter_distance/` only.

## What changed (v4 far polish)

DZ path unchanged when `in_danger_zone`. Far (100–200 m):

1. **GP-heavy triangulation** — size/span priors weak at range; cars GP weight 0.72, ped height prior 0.18; earlier honesty threshold.
2. **Lights/signs** — softer span vote in far (like DZ); honesty when span disagrees with GP.
3. **Finer parallax** on approach/recede (α=0.68) + stronger EMA hold when stable far.
4. **Focused far dataset** — `generate_far.py` → 96 seq (48 near / 48 outer), critical objs in 100–200 m + approach/recede; DZ/mid distractors to keep floors visible.
5. **Eval slices** — `far_100_200m` / `far_near_100_150m` / `far_outer_150_200m` + frozen DZ + held mid.

Files: `examples/distance_est/physics.py`, `eval_heuristic.py`, `generate_far.py`.

## Datasets

| set | sequences | split | notes |
|-----|-----------|-------|-------|
| baseline | 56 × 12 | 45 / 11 | bands ~5/50/100/200 |
| danger50 | 88 × 12 | 70 / 18 | DZ focus (frozen) |
| **far** | **96** × 12 | 77 / 19 | **100–150 + 150–200** critical |

## Metrics (CPU heuristic, GT-only post-hoc)

Predictor: `floor_scale_parallax_size_prior_closing_speed_v4_far`

### BEFORE (tip f70faa1 / v2_danger physics)

| slice | set | % correct | MAE |
|-------|-----|-----------|-----|
| far 100–200 m | far | **100.0%** | **4.653 m** |
| far_near 100–150 | far | 100.0% | 3.832 m |
| far_outer 150–200 | far | 100.0% | 5.540 m |
| far 100–200 | original | 100.0% | 5.440 m |
| far 100–200 | danger50 | 100.0% | 6.121 m |
| DZ 30–70 | all | **100.0%** | held |
| mid_near / mid_outer | all | **100.0%** | held |

### AFTER (v4 far polish)

| slice | set | % correct | MAE | note |
|-------|-----|-----------|-----|------|
| **far 100–200** | far | **100.0%** | **2.600 m** | MAE **−2.053 m** |
| far_near 100–150 | far | **100.0%** | **2.584 m** | −1.248 m |
| far_outer 150–200 | far | **100.0%** | **2.617 m** | −2.923 m |
| far 100–200 | original | **100.0%** | **4.563 m** | −0.877 m |
| far 100–200 | danger50 | **100.0%** | **2.684 m** | −3.437 m |
| **DZ 30–70** | original | **100.0%** | 1.491 m | **held** |
| **DZ 30–70** | danger50 | **100.0%** | 0.726 m | **held** |
| **DZ 30–70** | far | **100.0%** | 1.010 m | **held** |
| mid_near 5–30 | all | **100.0%** | held | **held** |
| mid_outer 70–100 | all | **100.0%** | held / slight MAE↓ | **held** |

Probe JSON:

- `data/video_synth/distance_est/far/EVAL_FAR_CPU.json`
- `data/video_synth/distance_est/far/EVAL_FAR_BEFORE.json`
- `data/video_synth/distance_est/far/EVAL_FAR_AFTER.json`
- `data/video_synth/distance_est/EVAL_FLOOR_SCALE_CPU.json`
- `data/video_synth/distance_est/danger50/EVAL_DANGER50_CPU.json`

Anti-contam: **CLEAN**.  
Caveat: synth pinhole invert can saturate tol@10/20% — MAE shows residual. **Not a VLM claim.** No quantum-advantage claim.

## Floor / freezes

- Shared tip router / scaffold paths: **not touched** → tip mixed floor re-smoke **N/A** (distance_est-only).
- Mixed (d) 1.0 / freezes ≥80%: **not abandoned**.
- **Freeze:** `codigo_vivo_tip_distance_far_100pct` — far % 100% with clear MAE win; DZ + mid held 100%.

## Adapters RO

- `data/lora_adapter/` mtime unchanged from worktree materialize — **no writes**.
- No new weights under `data/lora_adapter_distance/` (CPU-only).

## Commands

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-distance-far
python examples/distance_est/generate_far.py --n-seq 96 --seed 24092480
python examples/distance_est/eval_heuristic.py --data data/video_synth/distance_est/far --out-name EVAL_FAR_CPU.json
python examples/distance_est/eval_heuristic.py  # original; DZ must stay 100%
python examples/distance_est/eval_heuristic.py --data data/video_synth/distance_est/danger50 --out-name EVAL_DANGER50_CPU.json
python examples/distance_est/eval_heuristic.py --contam-self-test
```

## Non-goals

- No merge to main / tip / tip-cv.
- No CloudAgent.
- No write to `data/lora_adapter/`.
- No fold of mid / hardneg-r11 / hardneg-r12 / tti / motion-r4 / inverse-r3.
