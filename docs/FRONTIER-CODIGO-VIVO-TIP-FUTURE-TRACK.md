# FRONTIER — tip-future-track (future-pred / tracking polish)

**Branch:** `frontier/tip-future-track`  
**Base tip SHA:** `e70b23a` (`frontier/codigo-vivo-tip` @ R11; **side-only**)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-future-track` (Mac-111)  
**When:** 2026-09-24 ~14:13 ET  
**Freeze:** `codigo_vivo_tip_future_track_100pct_20260924_141347`  
**Scope:** Side-branch only — does **not** fold into tip / tip-cv / tip-tti / tip-distance-mid / tip-distance-far / tip-hardneg-r12/r13 / tip-inverse-r3 / tip-circ-expand.

## LOCK (Anthony)

- Scale = **building floors** ≈ 2.4–3.0 m. **NO fixed light heights.**
- Soft priors only: car ~4.5 m length, ped ~1.7 m height.
- **DANGER ZONE 30–70 m is FROZEN at 100%** (tip-distance-danger). Do not regress.
- Motion **100%**, collision **100%**, mixed **1.0** floors — untouched (distance_est-only).
- Target: **future-pred ± distance** (overall + DZ) where tip scoreboard showed gap below 100%.
- Tracking *association* already **100%** — held. Future *depth* tracking_only was the gap.
- GT only in `distances_gt.json` sidecars; never in prompts / memory / retrieval.
- Quantum `data/lora_adapter/` = **READ-ONLY**. New adapters → `data/lora_adapter_distance/` only.

## What changed (v5 future-track)

Distance **estimator** (`estimate_frame`) unchanged — DZ / overall distance floors identical MAE.

Future-pred only (`eval_future_pred` + physics helpers):

1. **`size_rate_next_distance`** — `d ∝ 1/s` next-depth from apparent growth (GT-free).
2. **`predict_future_distance_v5`** — high-conf: **median**(legacy closing-speed blend, size-rate, depth-vel).
3. **Low-conf fallback** — current-frame **ground-plane** via `estimate_via_floor_scale` (drops poisoned fake-apparent floor-scale projection that missed lights/signs).
4. **tracking_only path** — size-rate on `est_m` when present, else GP (was weak fake-apparent path @ ~86%).

Files: `examples/distance_est/physics.py`, `examples/distance_est/eval_heuristic.py`.  
Predictor tag: `floor_scale_parallax_size_prior_closing_speed_v5_future_track`.

## Metrics (CPU heuristic, GT-only post-hoc)

### BEFORE (tip e70b23a / v2_danger)

| slice | set | future track% | future +dist% |
|-------|-----|---------------|---------------|
| overall | original | 86.21 | 95.36 |
| DZ 30–70 | original | 91.08 | 97.30 |
| overall | danger50 | 89.89 | 98.12 |
| DZ 30–70 | danger50 | 89.66 | 96.59 |
| tracking assoc DZ | both | **100%** | — |
| distance DZ | both | **100%** | MAE 1.491 / 0.726 |

### AFTER (v5 future-track)

| slice | set | future track% | future +dist% | Δ track | Δ +dist |
|-------|-----|---------------|---------------|---------|---------|
| overall | original | **97.89** | **98.19** | **+11.68 pp** | **+2.83 pp** |
| DZ 30–70 | original | **100.0** | **100.0** | **+8.92 pp** | **+2.70 pp** |
| overall | danger50 | **99.77** | **99.77** | **+9.88 pp** | **+1.65 pp** |
| DZ 30–70 | danger50 | **100.0** | **100.0** | **+10.34 pp** | **+3.41 pp** |
| tracking assoc DZ | both | **100%** | — | held | — |
| distance DZ | both | **100%** | MAE **1.491 / 0.726** | **held** | MAE unchanged |

Probe JSON:

- `data/video_synth/distance_est/EVAL_FUTURE_BEFORE.json`
- `data/video_synth/distance_est/EVAL_FUTURE_AFTER.json`
- `data/video_synth/distance_est/danger50/EVAL_FUTURE_BEFORE.json`
- `data/video_synth/distance_est/danger50/EVAL_FUTURE_AFTER.json`

Anti-contam: **CLEAN** (self-test PASS).  
Caveat: synth pinhole invert can saturate tol@10/20% — MAE shows residual. **Not a VLM claim.** No quantum-advantage claim.

## Floor / freezes

- Shared tip router / scaffold / motion / collision paths: **not touched** → tip mixed / motion / collision re-smoke **N/A** (distance_est-only).
- Mixed (d) 1.0 / motion 100% / collision 100% / DZ 100%: **not abandoned**.
- **Freeze:** `codigo_vivo_tip_future_track_100pct` — clear future % win; DZ future → 100%; floors held.

## Adapters RO

- `data/lora_adapter/` mtime **2026-09-24 14:10:40 ET** (worktree materialize) — **no writes**.
- No new weights under `data/lora_adapter_distance/` (CPU-only).

## Commands

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-future-track
python examples/distance_est/eval_heuristic.py --out-name EVAL_FUTURE_AFTER.json
python examples/distance_est/eval_heuristic.py --data data/video_synth/distance_est/danger50 --out-name EVAL_FUTURE_AFTER.json
python examples/distance_est/eval_heuristic.py --contam-self-test
```

## Non-goals

- No merge to main / tip / tip-cv.
- No CloudAgent.
- No write to `data/lora_adapter/`.
- No fold of TTI / distance-mid / far / R12 / inv-r3 / R13 (fold queue stays with tip-cv).
