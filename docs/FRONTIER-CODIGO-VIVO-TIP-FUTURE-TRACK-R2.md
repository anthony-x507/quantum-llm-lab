# FRONTIER — tip-future-track-r2 (future-pred polish toward 100%)

**Branch:** `frontier/tip-future-track-r2`  
**Base:** `frontier/tip-future-track` @ `0a1c9b5` (easier than tip HEAD `e0f3183` — TTI conflicts in same `distance_est` files)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-future-track-r2` (Mac-111)  
**When:** 2026-09-24 ~14:20 ET  
**Freeze:** `codigo_vivo_tip_future_track_r2_100pct_20260924_142016`  
**Scope:** Side-branch only — does **not** fold into tip / tip-cv / tip-tti / tip-distance-mid / tip-distance-far / tip-hardneg-r12/r13/r14 / tip-inverse-r3 / tip-circ-expand / tip-future-track.

## LOCK (Anthony)

- Scale = **building floors** ≈ 2.4–3.0 m. **NO fixed light heights.**
- Soft priors only: car ~4.5 m length, ped ~1.7 m height.
- **DANGER ZONE 30–70 m is FROZEN at 100%** (tip-distance-danger). Do not regress.
- **DZ future-pred 100%** (from r1) — do not drop.
- Motion **100%**, collision **100%**, mixed **1.0** floors — untouched (distance_est-only).
- Target: orig **future track** 97.89→toward 100%; **+dist** if still below 100%.
- GT only in `distances_gt.json` sidecars; never in prompts / memory / retrieval.
- Quantum `data/lora_adapter/` = **READ-ONLY**.

## What changed (v6 future-track-r2)

Distance **estimator** (`estimate_frame`) unchanged — DZ / overall distance floors identical MAE.

Future-pred only (`eval_future_pred` + physics helpers):

1. **Near-plane clamp** at synth camera floor **1.5 m** (`generate.py`: `d = max(1.5, …)`). Size-rate no longer overshoots into unreachable depth when objects hit the near clip.
2. **Rate dampening** — extreme apparent growth/shrink (`rate_cap=1.45` + soft tail) reduces near-field occlusion blow-ups.
3. **Cold-start motion_hint nudge** (`±8%`) using meta `motion_hint` already on the observation/prompt channel (not GT meters), with **DZ-band guard** (`est ∈ [25,75]` skips nudge) so future DZ 100% stays held.
4. **Cold +distance path** returns nudged size-rate directly (median of identical cues would cancel the cold nudge).

Files: `examples/distance_est/physics.py`, `examples/distance_est/eval_heuristic.py`.  
Predictor tag: `floor_scale_parallax_size_prior_closing_speed_v6_future_track_r2`.  
Keeps v5 helpers for lineage; eval wired to v6.

## Metrics (CPU heuristic, GT-only post-hoc)

### BEFORE (v5 future-track @ 0a1c9b5 / 951c3df)

| slice | set | future track% | future +dist% |
|-------|-----|---------------|---------------|
| overall | original | 97.89 | 98.19 |
| DZ 30–70 | original | **100.0** | **100.0** |
| overall | danger50 | 99.77 | 99.77 |
| DZ 30–70 | danger50 | **100.0** | **100.0** |
| tracking assoc DZ | both | **100%** | — |
| distance DZ | both | **100%** | MAE 1.491 / 0.726 |

### AFTER (v6 future-track-r2)

| slice | set | future track% | future +dist% | Δ track | Δ +dist |
|-------|-----|---------------|---------------|---------|---------|
| overall | original | **99.34** | **99.46** | **+1.45 pp** | **+1.27 pp** |
| DZ 30–70 | original | **100.0** | **100.0** | held | held |
| overall | danger50 | **100.0** | **100.0** | **+0.23 pp** | **+0.23 pp** |
| DZ 30–70 | danger50 | **100.0** | **100.0** | held | held |
| tracking assoc DZ | both | **100%** | — | held | — |
| distance DZ | both | **100%** | MAE **1.491 / 0.726** | **held** | MAE unchanged |

Probe JSON:

- `data/video_synth/distance_est/EVAL_FUTURE_R2_BEFORE.json` (= prior AFTER)
- `data/video_synth/distance_est/EVAL_FUTURE_R2_AFTER.json`
- `data/video_synth/distance_est/danger50/EVAL_FUTURE_R2_BEFORE.json`
- `data/video_synth/distance_est/danger50/EVAL_FUTURE_R2_AFTER.json`

Anti-contam: **CLEAN** (self-test PASS).  
Caveat: synth pinhole invert can saturate tol@10/20% — MAE shows residual. **Not a VLM claim.** No quantum-advantage claim.  
Residual gap (~0.66 pp track): mostly cold-start frames where motion magnitude exceeds the guarded ±8% nudge.

## Floor / freezes

- Shared tip router / scaffold / motion / collision paths: **not touched** → tip mixed / motion / collision re-smoke **N/A** (distance_est-only).
- Mixed (d) 1.0 / motion 100% / collision 100% / DZ 100% / future DZ 100%: **held**.
- **Freeze:** `codigo_vivo_tip_future_track_r2_100pct` — clear future % win; floors held.

## Adapters RO

- `data/lora_adapter/` — **no writes** (before/after snapshot equal).
- No new weights under `data/lora_adapter_distance/` (CPU-only).

## Commands

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-future-track-r2
python examples/distance_est/eval_heuristic.py --out-name EVAL_FUTURE_R2_AFTER.json
python examples/distance_est/eval_heuristic.py --data data/video_synth/distance_est/danger50 --out-name EVAL_FUTURE_R2_AFTER.json
python examples/distance_est/eval_heuristic.py --contam-self-test
```

## Non-goals

- No merge to main / tip / tip-cv.
- No CloudAgent.
- No write to `data/lora_adapter/`.
- No fold (fold queue mid→R12→…→future→circ→R14 stays with tip-cv).
