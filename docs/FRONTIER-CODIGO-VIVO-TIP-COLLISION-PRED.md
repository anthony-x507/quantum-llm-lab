# FRONTIER — tip-collision-pred (predictive collision layer)

**Branch:** `frontier/tip-collision-pred`  
**Base tip SHA:** `d892398` (`frontier/codigo-vivo-tip`)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-collision-pred` (Mac-111)  
**When:** 2026-09-24 13:09:21 ET  
**Scope:** Side-branch only — does **not** touch tip-cv / tip-hardneg-r8 / tip-distance-danger / tip-scaffold-motion.

## LOCK (Anthony 2026-09-24)

- Model evaluates **hypothetical actions** + **physical consequences** (brake→rear-end? turn→pedestrian?).
- Collision physics: trajectories, velocities, **masses** (elastic 2D disks).
- Integrate with inverse planning (ablation), floor-scale distance (consume stubs), WorkingMemory.
- Emit: `chosen_action` + `predicted_consequence` + `is_safe`.
- Metric: **% correct collision preds** vs real-frame GT (post-hoc sidecars only).
- Anti-contam: real consequences **NEVER** at inference (GT only for eval).
- Quantum `data/lora_adapter/` = **READ-ONLY**. New adapters → `data/lora_adapter_collision/` only.
- Distance-danger 100% @ 30–70 m on `frontier/tip-distance-danger` `110bcbc` — **do not reimplement**; consume estimates via stubs.

## What this branch adds

1. **`distance_consumer.py`** — stub-safe DistanceEstimate Protocol; urgency bands incl. **DANGER ZONE 30–70 m**; refuses `gt_*` / `distances_gt` / `consequences_gt`.
2. **Memory bridge** — emit may carry `distance_note` / `distance_urgency_max` / `distance_partner_band` into WorkingMemory (perception only).
3. **Eval harness** — attaches arena-px proxy estimates at inference (stand-in until distance branch merges); physics oracle scoring unchanged; tip probe JSON.
4. Re-smoke CPU synth: **40** sequences (32 train / **8** eval), horizons k=1,3,5.

Does **not** import unmerged `examples/distance_est` changes from tip-distance-danger.

## Metrics (CPU physics oracle, GT-only post-hoc)

Source: `data/collision_predictive/EVAL_COLLISION_CPU.json`  
Probe: `data/frontier_tip_collision_pred_probe.json`  
Audit: `data/eval_audit/collision_20260924_130857.jsonl`

| predictor | k=1 | k=3 | k=5 | overall |
|-----------|-----|-----|-----|---------|
| **collision_physics** | **100.0** | **100.0** | **100.0** | **100.0** |
| inverse_cv (no collision) | 94.05 | 85.95 | 75.68 | 85.23 |
| collision_choose_safest | 100.0 | 100.0 | 100.0 | 100.0 |

- **n_eval_seqs = 8** · **n_queries = 555** (action-conditional × horizons)
- **Ablation (collision − inverse_cv): +14.77 pp**
- Contam self-test: **PASS** (inject GT → INVALID)
- Retrieval train∩eval leak: **∅**
- `physics_fail_rate` k=5 ≈ 0.0054 (edge); overall oracle **100%**

### Honest interpretation

World **is** the elastic-disk simulator → `collision_physics` @ 100% is the **CPU oracle / own-delta floor** for a future VLM. **Not** a VLM claim. No quantum-advantage claim. Distance cues are perception urgency only — they do not replace GT scoring.

## Floor / freezes

- Shared tip router / scaffold paths: **not touched** → tip floor re-smoke **N/A**.
- Mixed (d) / freezes ≥80%: **not abandoned** (this branch is collision_predictive-only).
- Metric ≥80% → freeze written under `data/freeze_manifests/`.

## Adapters RO

- `data/lora_adapter/` mtime **2026-09-24 13:07:53 ET** — **no writes** from this fold (baseline held).
- `data/lora_adapter_collision/` empty (VLM deferred).

## Commands

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-collision-pred
/Users/anthony/Documents/quantum-llm-lab/.venv/bin/python examples/collision_predictive/generate.py --n-seq 40 --seed 24092445
/Users/anthony/Documents/quantum-llm-lab/.venv/bin/python examples/collision_predictive/eval_harness.py --contam-self-test
```

## Non-goals

- No merge to `main` / tip-cv.
- No CloudAgent.
- No write to `data/lora_adapter/`.
- No reimplementation of distance-danger floor-scale physics.
- No R8 / hardneg fold.
