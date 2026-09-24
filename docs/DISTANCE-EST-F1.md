# Distance estimation — Fase 1 (FLOOR-SCALE CPU)

**When:** 2026-09-24 ~04:54 ET (Mac-139)  
**Scale lock:** FLOOR-SCALE — building floors 2.4–3.0 m — **NO fixed object heights**  
**Family:** `data/video_synth/distance_est/` (temporal street; extends video_synth)  
**Not:** inverse_planning corridor · quantum adapter  
**Prototype:** `examples/distance_est/`

## Method

1. Buildings expose `n_floors` + `floor_height_m` (standard 2.4–3.0 m) + `floor_px` in **meta** (scale ref, not distance GT).
2. Heuristic: calibrate `d_building` from facade floors → ground-plane depth from `cy` anchored by floor-scale; lights/signs may use floor-span derived height when coplanar with facade.
3. Lights in synth have **varied** true height **3–5 m** (estimator must not assume 3 m).
4. Priority distances: cars, intersections, stop signs, pedestrians, lights.
5. Parallax refine: growing→approach, shrinking→recede.
6. GT meters only in `distances_gt.json` — post-hoc compare.

## Dataset

| item | value |
|------|-------|
| generator | `examples/distance_est/generate.py` |
| sequences | **56** × 12 frames |
| split | train **45** / eval **11** |
| bands | ~5 / 50 / 100 / 200 m |
| classes | building, light, car, pedestrian, stop_sign, intersection |
| adapter | `data/lora_adapter_distance/` (GPU deferred) |

## CPU heuristic metrics (`EVAL_FLOOR_SCALE_CPU.json`)

Predictor: `floor_scale_parallax_heuristic` · anti-contam **CLEAN**

| band | n | % correct | tol |
|------|---|-----------|-----|
| ~5m | 528 | **76.33%** | ±10% |
| ~50m | 536 | **48.69%** | ±10%/±20% |
| ~100m | 473 | **76.74%** | ±20% |
| ~200m | 275 | **56.73%** | ±20% |
| **overall** | 1812 | **65.29%** | |

### Ablation — tracking

| mode | n | % correct |
|------|---|-----------|
| tracking-only | 1903 | 100.0% |
| tracking + floor-calibrated distance | 1900 | 100.0% |

Synth tracks are easy (few crossings) → both saturate. Distance gate does not hurt.

### Ablation — future depth prediction (camera-axis; not corridor inverse_planning)

| mode | depth-pred % | position-pred % |
|------|--------------|-----------------|
| tracking-only | **73.51%** | 99.58% |
| + floor-calibrated distance rate | **64.24%** | 99.58% |

Honest: hold-last depth beats noisy velocity on this CPU heuristic; VLM/LoRA Δ deferred (GPU busy).

## Anti-contam

- Audit: `data/eval_audit/distance_20260924_045444.jsonl`
- Self-test: `data/video_synth/distance_est/ANTI_CONTAM_SELFTEST.json` (passed)
- Dirty → INVALID discard+rerun

## GPU

Staged queue script: `data/RUN_DISTANCE_EST_WHEN_FREE.sh` (behind ent/classical/video_f1; **not** launched as extra screen this cycle).  
Quantum `data/lora_adapter/` **RO** — mtime untouched.
