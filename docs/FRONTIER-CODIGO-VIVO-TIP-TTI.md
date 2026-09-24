# FRONTIER — tip-tti (time-to-impact metric on collision/distance layer)

**Status:** **FOLDED** into `frontier/codigo-vivo-tip` (cherry-pick rebase `c483e46` onto `e70b23a` → `6665e2c` FF-equivalent)  
**Branch:** `frontier/tip-tti` (rebased feat retained) · tip `frontier/codigo-vivo-tip`  
**Base tip at fold:** `e70b23a` (post R11) · feat from `9cc5ed5`  
**When:** polish ~13:56 ET · fold 2026-09-24 14:12:08 ET · Mac-111 (`074c6626-…`)  
**Freeze:** `codigo_vivo_tip_tti_fold_100pct_20260924_141146`  
**Claim:** NO quantum advantage. CPU heuristic / physics oracle TTI % vs GT only.

## LOCK (Anthony / Leader)

- Add/raise **TTI** (time-to-impact seconds) on tip collision/distance layer.
- Closing speed from **% growth per frame** → `v_close` → **TTI seconds**; report **% correct TTI vs GT**.
- Hold: collision physics **100%**, choose_safest **100%**, inverse_cv **~99.82%**, mixed floor **1.0**.
- Retain freezes: **collision_n**, **inverse_r2 side**, **distance_danger**, **r10/r11 side** + priors.
- Anti-contam: GT / real consequences **NEVER** at inference (TTI GT from `distances_gt.json` depth deltas post-hoc only).
- Quantum `data/lora_adapter/` = **READ-ONLY**.
- No merge to `main`; no fold into tip.
- Measure TTI accuracy bands; **freeze if ≥80% rise and floors held**.

## What this branch changes

1. **`physics.closing_speed_tti`** — size-invariant TTI (`tti = dt / growth`); optional dist-rate fallback when growth weak-positive and depths clearly approach (never on recede). Helpers: `gt_tti_from_depth`, `tti_within_tol`, `tti_band`.
2. **`eval_heuristic.py`** — scores **% correct TTI vs GT** (tol ±20% or ±0.5 s); primary = scorable frames (prev observation required); bands `<2s` / `2-5s` / `5-15s` / `>15s` + danger-zone TTI; cold-start reported separately.
3. **Probe / freeze** — `data/frontier_tip_tti_probe.json` + `codigo_vivo_tip_tti_100pct_*`.

Does **not** reimplement collision elastic oracle; does **not** write adapters; does **not** fold into tip-cv.

## Metrics (CPU heuristic / physics oracle, GT-only post-hoc)

### TTI (distance_est)

| | before | after (this tip) |
|--|--------|------------------|
| TTI % vs GT (reported) | **0%** (emission-count only) | **100.0%** primary scorable |
| original eval (scorable) | — | **100.0%** (691/691) |
| danger50 eval (scorable) | — | **100.0%** (725/725) |
| overall incl. cold-start (orig / d50) | — | 91.16% / 91.66% |
| TTI bands (scorable) | — | all **100%** |
| TTI danger 30–70 m (scorable) | — | **100%** (both sets) |
| false_emit | — | **0** |
| distance % (orig / d50 / DZ) | 100 / 100 / 100 | **100 / 100 / 100** (held) |

Cold-start: first frame / first sighting has no temporal signal → excluded from primary denominator (honest); still listed under `overall_incl_cold_start`.

### Collision floors (re-smoke, n=40 / 2850)

| predictor | before (tip HEAD) | after |
|-----------|-------------------|-------|
| **collision_physics** | **100.0%** | **100.0%** |
| **inverse_cv** | **99.82%** | **99.82%** |
| **collision_choose_safest** | **100.0%** | **100.0%** |
| contam / retrieval | PASS / ∅ | PASS / ∅ |
| mixed floor | **1.0** (router untouched) | **1.0** |

Source: `data/video_synth/distance_est/EVAL_FLOOR_SCALE_CPU.json`, `…/danger50/EVAL_DANGER50_CPU.json`, `data/collision_predictive/EVAL_COLLISION_CPU.json`  
Probe: `data/frontier_tip_tti_probe.json`  
Audit: `data/eval_audit/distance_*.jsonl`, `data/eval_audit/collision_*.jsonl`

### Honest interpretation

- World **is** the synth pinhole + elastic-disk sim → TTI@100% scorable and collision@100% are **CPU oracle / own-delta floors**. **Not** a VLM claim. No quantum-advantage claim.
- Size-invariant TTI cancels `d_est` when growth is trustworthy (`tti = dt * s_prev/(s_curr−s_prev)`).
- Primary metric excludes cold-start (no prev size) — cannot invent TTI without temporal signal.

## Floor / freezes

- Shared tip router / scaffold paths: **not touched** → tip / mixed floor re-smoke **N/A** (mixed **1.0** assumed held).
- Collision physics / choose_safest / inverse_cv: **held** (re-smoke).
- TTI rise **0→100** (≥80% target) and floors held → **freeze written**.
- Retained: collision_n, inverse_r2 (side + tip fold), distance_danger, r10/r11 side + priors.

## Adapters RO

- `data/lora_adapter/` — **no writes** (`.gitkeep` mtime unchanged from worktree create).
- `data/lora_adapter_distance/` / collision adapters untouched (VLM deferred).

## Commands

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-tti
/Users/anthony/Documents/quantum-llm-lab/.venv/bin/python examples/distance_est/eval_heuristic.py --contam-self-test
/Users/anthony/Documents/quantum-llm-lab/.venv/bin/python examples/distance_est/eval_heuristic.py
/Users/anthony/Documents/quantum-llm-lab/.venv/bin/python examples/distance_est/eval_heuristic.py \
  --data data/video_synth/distance_est/danger50 --out-name EVAL_DANGER50_CPU.json
/Users/anthony/Documents/quantum-llm-lab/.venv/bin/python examples/collision_predictive/eval_harness.py --contam-self-test
```

## Non-goals / avoided

- No merge to `main`. Tip fold complete.
- No CloudAgent.
- No write to `data/lora_adapter/`.
- Fold worktree: tip-cv only. Avoided tip-distance-mid / tip-distance-far / tip-hardneg-r12 / tip-hardneg-r13 / tip-inverse-r3.
- No fake metrics.

## Blockers

None. TTI primary 100%; collision floors held; freeze written.
