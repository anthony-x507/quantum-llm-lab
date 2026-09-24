# FRONTIER — tip-future-track-r3 (near-field cold motion_hint polish)

**Branch:** `frontier/tip-future-track-r3`  
**Base:** `frontier/tip-future-track-r2` @ `6dab62d` (feat `ba5f2cf`)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-future-track-r3` (Mac-111)  
**When:** 2026-09-24 ~14:28 ET  
**Freeze:** `codigo_vivo_tip_future_track_r3_100pct_20260924_142834`
**Feat SHA:** `6da80e5` (`6da80e5361607209aa19fbe44467f9a663a26c64`)
**Scope:** Side-branch only — does **not** fold into tip / tip-cv / tip-tti / tip-distance-mid / tip-distance-far / tip-hardneg-r12/r13/r14/r15 / tip-inverse-r3 / tip-circ-expand / tip-future-track / tip-future-track-r2.

## LOCK (Anthony)

- Scale = **building floors** ≈ 2.4–3.0 m. **NO fixed light heights.**
- Soft priors only: car ~4.5 m length, ped ~1.7 m height.
- **DANGER ZONE 30–70 m is FROZEN at 100%** (tip-distance-danger). Do not regress.
- **DZ future-pred 100%** (from r1/r2) — do not drop.
- Motion **100%**, collision **100%**, mixed **1.0** floors — untouched (distance_est-only).
- Target: orig **future track** 99.34→toward 100%; **+dist** rise or hold.
- GT only in `distances_gt.json` sidecars; never in prompts / memory / retrieval.
- Quantum `data/lora_adapter/` = **READ-ONLY**.

## What changed (v7 future-track-r3)

Distance **estimator** (`estimate_frame`) unchanged — DZ / overall distance floors identical MAE.

Future-pred only (`eval_future_pred` + physics helpers), building on v6:

1. **Class-aware cold motion_hint step** (obs-channel `motion_hint` + `class` only — not GT meters):
   - **Movable** (`car`, `pedestrian`) with `est < 7 m`: step **±12%** (was flat ±8%). Near-field relative depth rates are larger; blank ±8% under-nudges true movers.
   - **Staticish landmarks** (`intersection`, `stop_sign`, `light`): step **±4%**. Their `approach`/`recede` labels often reflect ego-motion with tiny true depth change; flat ±8% overshoots.
   - **Far / default**: keep v6 **±8%**.
2. **DZ-band guard** (`est ∈ [25,75]` skips nudge) + **near-plane clamp 1.5 m** + **rate dampen** retained from v6.

Files: `examples/distance_est/physics.py`, `examples/distance_est/eval_heuristic.py`.  
Predictor tag: `floor_scale_parallax_size_prior_closing_speed_v7_future_track_r3`.  
Keeps v5/v6 helpers for lineage; eval wired to v7.

## Metrics (CPU heuristic, GT-only post-hoc)

### BEFORE (v6 future-track-r2 @ 6dab62d / ba5f2cf)

| slice | set | future track% | future +dist% |
|-------|-----|---------------|---------------|
| overall | original | 99.34 | 99.46 |
| DZ 30–70 | original | **100.0** | **100.0** |
| overall | danger50 | **100.0** | **100.0** |
| DZ 30–70 | danger50 | **100.0** | **100.0** |
| tracking assoc DZ | both | **100%** | — |
| distance DZ | both | **100%** | MAE 1.491 / 0.726 |

### AFTER (v7 future-track-r3)

| slice | set | future track% | future +dist% | Δ track | Δ +dist |
|-------|-----|---------------|---------------|---------|---------|
| overall | original | **99.58** | **99.64** | **+0.24 pp** | **+0.18 pp** |
| DZ 30–70 | original | **100.0** | **100.0** | held | held |
| overall | danger50 | **100.0** | **100.0** | held | held |
| DZ 30–70 | danger50 | **100.0** | **100.0** | held | held |
| tracking assoc DZ | both | **100%** | — | held | — |
| distance DZ | both | **100%** | MAE **1.491 / 0.726** | **held** | MAE unchanged |

Probe JSON:

- `data/video_synth/distance_est/EVAL_FUTURE_R3_BEFORE.json` (= r2 AFTER)
- `data/video_synth/distance_est/EVAL_FUTURE_R3_AFTER.json`
- `data/video_synth/distance_est/danger50/EVAL_FUTURE_R3_BEFORE.json`
- `data/video_synth/distance_est/danger50/EVAL_FUTURE_R3_AFTER.json`

Anti-contam: **CLEAN** (self-test PASS).  
Caveat: synth pinhole invert can saturate tol@10/20% — MAE shows residual. **Not a VLM claim.** No quantum-advantage claim.  
Residual gap (~0.42 pp track): remaining cold/warm near-plane frames where true depth change exceeds any safe obs-channel step (no magnitude on `motion_hint`; size-rate disagrees with GT near the 1.5 m clamp). **Plateau without GT leak** — do not invent `_v_depth` / sidecar meters into the predictor.

## Floor / freezes

- Shared tip router / scaffold / motion / collision paths: **not touched** → tip mixed / motion / collision re-smoke **N/A** (distance_est-only).
- Mixed (d) 1.0 / motion 100% / collision 100% / DZ 100% / future DZ 100%: **held**.
- **Freeze:** `codigo_vivo_tip_future_track_r3_100pct` — clear future % win; floors held.

## Adapters RO

- `data/lora_adapter/` — **no writes** (before/after snapshot equal).
- No new weights under `data/lora_adapter_distance/` (CPU-only).

## Commands

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-future-track-r3
python examples/distance_est/eval_heuristic.py --out-name EVAL_FUTURE_R3_AFTER.json
python examples/distance_est/eval_heuristic.py --data data/video_synth/distance_est/danger50 --out-name EVAL_FUTURE_R3_AFTER.json
python examples/distance_est/eval_heuristic.py --contam-self-test
```

## Non-goals

- No merge to main / tip / tip-cv.
- No CloudAgent.
- No write to `data/lora_adapter/`.
- No fold (fold queue prefers r2 or r3-if-better over r1; fold itself stays with tip-cv).
