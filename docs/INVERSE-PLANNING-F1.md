# Inverse planning — Fase 1 (passive) results

**Domain lock:** separate from street-lights video F1, classical scenes, and quantum.
Quantum `data/lora_adapter/` = **READ-ONLY**. No quantum-advantage claims.
Anti-contamination on: GT futures only in sidecars; never in prompts.

Timestamp: **2026-09-24 04:45 ET** (Mac-139).

## Scene choice (documented)

**Top-down corridor arena** — colored balls + boxes slide with elastic wall
bounces; **one** discrete corridor signal panel (red/amber/green).

Deliberately **not** street-F1 (no cars / multi-light intersection), **not**
classical sport/projectile stills, **not** quantum circuits.

See `data/inverse_planning/SCENE_CHOICE.md`.

## Dataset

| Item | Value |
|------|-------|
| Generator | `examples/inverse_planning/generate_passive.py` |
| Path | `data/inverse_planning/` |
| Seed | 240924 |
| Sequences | **40** (train **32** / eval **8**) |
| Frames/seq | 10–20 |
| Horizons k | 1, 3, 5 |
| GT futures | `futures_gt.json` sidecars only (`meta.json` has none) |
| Retrieval index | `retrieval_index_train.json` — **train only**, leak=∅ |
| Adapter (later) | `data/lora_adapter_inverse/` **NEW dir only** |

## Fase 1 numbers — constant-velocity baseline (CPU)

GPU held by `qlora-ent` (+ classical / video_f1 queued) → **no LoRA / no VLM**.
Deterministic CV + wall-bounce predictor; physics gate applied.

Source: `data/inverse_planning/EVAL_PASSIVE_CV.json`  
Audit: `data/eval_audit/inverse_20260924_044542.jsonl` (prompt touches, **no GT**)

| k | n queries | pos_acc (±8px) | physics_fail_rate | signal_acc (hold-last) | mean_dist px |
|---|-----------|----------------|-------------------|------------------------|--------------|
| 1 | 112 | **1.000** | **0.000** | 0.500 | ~0.00 |
| 3 | 96 | **1.000** | **0.000** | 0.000 | ~0.00 |
| 5 | 80 | **1.000** | **0.000** | 0.512 | ~0.00 |

Interpretation (honest):
- World **is** CV+bounce → CV baseline matches positions (own-delta floor for VLM later).
- Signal hold-last is weak (schedule unknown) — expected; not the primary metric.
- `physics_fail_rate=0` for CV is correct; gate still flags bad preds (see below).

### Physics-law gate self-test

`data/inverse_planning/PHYSICS_GATE_SELFTEST.json` — **PASS**

| Injected failure | Flagged | reason |
|------------------|---------|--------|
| teleport jump | yes | `teleport` |
| outside arena | yes | `wall_phase_or_flying` |
| honest CV step | no | — |

Rule: teleport / flying → `physics_fail` **even if** position luckily near GT.

### Anti-contam self-test

Injecting future GT into prompt → **INVALID** (`passed=true`).
Clean prompts / `meta.json` contain **no** futures.

## Paths

```
examples/inverse_planning/
  generate_passive.py
  eval_passive.py
  physics.py
  README.md
data/inverse_planning/          # frames local (gitignored); SUMMARY+EVAL tracked
data/lora_adapter_inverse/      # empty .gitkeep — VLM/LoRA when GPU free
data/eval_audit/inverse_*.jsonl
docs/LOCK-INVERSE-PLANNING.md
docs/INVERSE-PLANNING-F1.md     # this file
```

## Stub for Leader — cross vs quantum “anticipate error”

> **Do not mix adapters or GT.** When quantum entanglement / anticipate-error
> numbers exist on their own lane, Leader may **compare tables side-by-side**
> (inverse F1 pos_acc / phys_fail by k  vs  quantum anticipate metrics).
> This note is a placeholder only — no shared retrieval, no shared LoRA, no
> shared scenes. Inverse reports only `data/lora_adapter_inverse/` (future);
> quantum stays on `data/lora_adapter/` RO.

## Sketch — Fase 2 / Fase 3 (docs only, no train yet)

### Fase 2 — action-conditional prediction
- Input: history 0..N **plus** a hypothetical action `a` (e.g. toggle signal,
  impulse on one object).
- Target: state at N+k **under** that action (simulator rolls forward with `a`).
- GT still sidecar-only. Metric: same pos_acc / phys_fail by k, plus
  action-sensitivity (prediction must change when `a` changes).

### Fase 3 — choose action for planning
- Model proposes action `a*` to maximize predicted correctness / goal
  (e.g. keep ball in zone, match desired signal).
- Eval: execute `a*` in simulator; score realized N+k vs goal.
- Still no GT in the loop; physics gate remains hard fail.

## Related — collision predictive (2026-09-24 ~05:05)

Runnable CPU **action-conditional** cousin: `examples/collision_predictive/` (merge-lane elastic disks). Ablation: collision layer **+14.8 pp** vs inverse-style CV on safety/consequence prediction. Does not overwrite this corridor F1 set.

## Next (GPU free)

1. VLM base zero-shot on eval prompts → own-delta vs CV floor.
2. LoRA train → `data/lora_adapter_inverse/` only (never quantum/classical/video_f1 adapters).
3. Re-eval + physics gate; reinforce what works; continue permanent cycle.
