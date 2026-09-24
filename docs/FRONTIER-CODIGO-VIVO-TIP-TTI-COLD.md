# FRONTIER — tip-tti-cold (raise TTI overall+cold-start)

**Status:** **FOLDED** into `frontier/codigo-vivo-tip`  
**Branch:** `frontier/tip-tti-cold` → tip `frontier/codigo-vivo-tip`  
**Worktree (fold):** `/Users/anthony/Documents/quantum-llm-lab-tip-cv` (Mac-111)  
**Base tip:** `677235a` (post R16 fold)  
**Side:** `c97e89a` / feat `9ddb8f4` (based on tip `4bfc924` post inverse-r3)  
**When:** side ~14:35 ET · fold 2026-09-24 15:28:50 ET  
**Freeze (side):** `codigo_vivo_tip_tti_cold_100pct_20260924_143601`  
**Freeze (fold):**   
**Fold feat SHA:**  ()`codigo_vivo_tip_tti_cold_fold_100pct_20260924_152850`  
**Claim:** NO quantum advantage. CPU heuristic / soft priors only.

## LOCK (Anthony / Leader)

- Raise **TTI overall incl. cold-start** (~91% post tip-tti) toward 100%.
- Retain cold rise (~91→~95%); **do NOT chase residual ~5% plateau**.
- Hold: TTI scorable **100%**, distance DZ **100%**, mixed **1.0**, R16 **52/52**, R15 **52/52**, choose_n n=80 @**100%**, LP/pillars/circ.
- Anti-contam: GT / `v_depth` / real consequences **NEVER** at inference.
- Quantum `data/lora_adapter/` = **READ-ONLY**.
- No merge to `main`. **Do NOT fold R17+** this task.
- Freeze if retained ≥80% of side rise **or** plateau hold at ~95%.

## What this fold ports

1. **`physics.cold_start_tti`** — when no prev observation and obs-channel `motion_hint==approach`, emit TTI from soft class closing-speed priors (`tti = d_est / v_prior`). Near movables (`car`/`pedestrian`, `d_est < 8 m`) use short absolute TTI prior `0.8 s` (tol ±0.5 s covers sub-second GT).
2. **`eval_heuristic.estimate_frame`** — wires cold path as `+tti_cold` (scorable growth/dist-rate path untouched).
3. Predictor tag → tip `…_v7_future_track_r3_tti_cold` / TTI `…_v4_tti_cold` (keeps tip future-track-r3 stack).

Does **not** reopen future-track files; does **not** write adapters; does **not** fold R17+.

### Soft priors (m/s)

| class | v_close prior |
|-------|---------------|
| car | 18.0 |
| pedestrian | 8.0 |
| light / intersection | 6.0 |
| stop_sign | 2.4 |

## Metrics (CPU heuristic, GT-only post-hoc) — tip after fold

### TTI

| | before (tip @ 677235a) | after (fold) |
|--|------------------------|--------------|
| TTI scorable orig | **100%** (691/691) | **100%** (691/691) held |
| TTI scorable danger50 | **100%** (725/725) | **100%** (725/725) held |
| overall+cold orig | 91.16% | **94.99%** (**+3.83 pp**; side rise retained **100%**) |
| overall+cold danger50 | 91.66% | **94.82%** (**+3.16 pp**; side rise retained **100%**) |
| TTI DZ scorable | **100%** | **100%** held |
| false_emit | 0 | **0** |
| distance DZ | **100%** | **100%** held |

Cold frames: all t=0 + `motion_hint=approach` (orig 67 / d50 66). Soft priors recover ~43% / ~38% of cold; remainder is multi-modal `v_close` without temporal signal (**plateau without GT leak** — Anthony lock: STOP chasing).

### Floors (re-smoke on tip)

| Surface | after fold |
|---------|------------|
| mixed (d) unified | **1.0** |
| R16 router / verifier | **52/52 · 44/44** |
| R15 router | **52/52** |
| LP router | **64/64** |
| pillars / circ / smoke | **37/37 · 5/5 · 12/12** |
| choose_safest n=80 | **100%** (5670 queries) |
| collision_physics | **100.0%** |
| inverse_cv @ n80 | **99.89%** |
| `ent_never_on_python` / `wired_to_vlm` | **true** / **true** |
| adapters RO mtime | **unchanged** (1790261820) |

Anti-contam: **CLEAN**.

## Floor / freezes

- Clear cold rise retained (100% of side) + floors held → **fold freeze written**.
- Plateau ~95% / ~5% residual → **freeze and STOP** (do not chase).
- **FOLDED** into tip / tip-cv.

## Adapters RO

- `data/lora_adapter/` — **no writes** (`.gitkeep` mtime unchanged across edits/evals).

## Method

Merge-port side feat `9ddb8f4` onto tip `677235a` (keep tip v7 future_track estimator; layer cold_start_tti). Tip worktree only. No merge main. No Cloud Agents. R17+ not folded.

## Blockers / plateau note

None for freeze. Residual cold gap is plateau-safe without temporal signal / GT leak — do not invent sidecar `v_depth` into the predictor. **Next (not this task):** R17 @ `970fc4a`.
