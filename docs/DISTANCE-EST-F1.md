# Distance estimation — Fase 1 + DANGER ZONE 50 m reinforce

> **v4 far polish (2026-09-24, folded into tip):** GP-heavy far 100–200 m + finer parallax/EMA. Far-set MAE **4.653→2.600 m** (side); re-smoke on tip after fold. DZ + mid held 100%. See `docs/FRONTIER-CODIGO-VIVO-TIP-DISTANCE-FAR.md`.


> **v2 polish (2026-09-24 ~13:05 ET, branch `frontier/tip-distance-danger`):** GP-first lights/signs + multi-building floor-scale + honesty + finer parallax/EMA. Original DZ 30–70 m **49.72% → 100%** (+51.31 pp vs baseline 48.69); danger50 DZ **60.11% → 100%**; future-pred DZ +dist improves (orig 48.55→97.3; danger50 61.69→96.59). MAE DZ 1.49 m / 0.73 m. See `docs/FRONTIER-CODIGO-VIVO-TIP-DISTANCE-DANGER.md`. Caveat: synth pinhole invert can saturate tol — not VLM.


**When:** 2026-09-24 ~04:54 ET baseline (`bcbcdc8`); ~05:12 ET danger50 reinforce (Mac-139)  
**Scale lock:** FLOOR-SCALE — building floors 2.4–3.0 m — **NO fixed light heights**  
**Soft priors (eval):** car length ~4.5 m · ped height ~1.7 m  
**Family:** `data/video_synth/distance_est/` (+ `danger50/` focused set)  
**Not:** inverse_planning corridor · quantum adapter  
**Prototype:** `examples/distance_est/`

## Method

1. Buildings expose `n_floors` + `floor_height_m` (standard 2.4–3.0 m) + `floor_px` in **meta** (scale ref, not distance GT).
2. Heuristic: floor-scale `d_building` → ground-plane depth from `cy`; **cars/peds** triangulate with soft size priors; lights/signs use floor-span derived height when coplanar (never fixed 3 m).
3. Fine parallax refine (stronger weight in 30–70 m) + **closing-speed / TTI** from apparent growth.
4. Priority distances: cars, intersections, stop signs, pedestrians, lights.
5. GT meters only in `distances_gt.json` — post-hoc compare.

## Datasets

| set | generator | sequences | split | focus |
|-----|-----------|-----------|-------|-------|
| baseline | `generate.py` | **56** × 12 | 45 / 11 | bands ~5/50/100/200 |
| **danger50** | `generate_danger50.py` | **88** × 12 | 70 / 18 | critical obj in **30–70 m** + approach/recede |

Adapter: `data/lora_adapter_distance/` (GPU deferred).

## CPU metrics — original eval set (improved estimator)

Predictor: `floor_scale_parallax_size_prior_closing_speed` · anti-contam **CLEAN**

| band | n | % correct | Δ vs bcbcdc8 |
|------|---|-----------|--------------|
| ~5m | 528 | 75.76% | −0.57 pp |
| **~50m** | 536 | **50.56%** | **+1.87 pp** (was 48.69%) |
| ~100m | 473 | 79.28% | +2.54 pp |
| ~200m | 275 | 60.73% | +4.00 pp |
| **overall** | 1812 | **66.94%** | **+1.65 pp** (was 65.29%) |

| slice | n | % correct | Δ vs baseline 48.69% |
|-------|---|-----------|----------------------|
| **30–70 m DANGER ZONE** | 527 | **49.72%** | **+1.03 pp** |

### Ablation — tracking (original)

| mode | overall | danger zone |
|------|---------|-------------|
| tracking-only | 100.0% | 100.0% |
| tracking + distance | 100.0% | 100.0% |

### Ablation — future depth pred (original)

| mode | overall depth-pred | danger-zone depth-pred |
|------|--------------------|------------------------|
| tracking-only | 73.57% | 64.11% |
| + distance / closing-speed | 65.02% | 48.55% |

Honest: on mixed original set, +distance still hurts future-pred in danger zone (noisy mid-band).

## CPU metrics — danger50 focused eval (18 seq)

| band / slice | n | % correct | Δ vs baseline 48.69% |
|--------------|---|-----------|----------------------|
| ~50m band | 1012 | **62.15%** | **+13.46 pp** |
| **30–70 m DANGER ZONE** | 915 | **60.11%** | **+11.42 pp** |
| overall | 1920 | 73.54% | — |

### Ablation — danger50 (future pred **improves** in zone)

| mode | overall depth-pred | danger-zone depth-pred |
|------|--------------------|------------------------|
| tracking-only | 68.92% | 60.05% |
| + distance / closing-speed | **74.32%** | **61.69%** |

Tracking±distance saturates at 100% (synth, few crossings). On the focused mid-band set, distance **helps** inverse-style future pred (+5.4 pp overall, +1.64 pp in zone).

## Anti-contam

- Original audit: `data/eval_audit/distance_20260924_051251.jsonl` — **CLEAN**
- Danger50 audit: `data/eval_audit/danger50_20260924_051252.jsonl` — **CLEAN**
- Self-tests: both `ANTI_CONTAM_SELFTEST.json` **passed**
- Dirty → INVALID discard+rerun

## GPU

Staged queue: `data/RUN_DISTANCE_EST_WHEN_FREE.sh` (behind ent/classical/video_f1).  
Quantum `data/lora_adapter/` **RO** — mtime **00:58:09** untouched.
