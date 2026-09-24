# Predictive collision — Fase 1 (CPU) results

**Domain lock:** top-down merge lane (ego + vehicles/pedestrians with mass).
Not street-F1, not inverse corridor balls, not quantum.
Quantum `data/lora_adapter/` = **READ-ONLY**.

Timestamp: **2026-09-24 05:05 ET** (Mac-139).

## Dataset

| Item | Value |
|------|-------|
| Generator | `examples/collision_predictive/generate.py` |
| Path | `data/collision_predictive/` |
| Seed | 24092445 |
| Sequences | **40** (train **32** / eval **8**) |
| Actions | coast, brake, accelerate, turn_left, turn_right |
| Horizons k | 1, 3, 5 |
| GT | `consequences_gt.json` sidecars only |
| Retrieval | `retrieval_index_train.json` — train only, leak=∅ |
| Adapter (later) | `data/lora_adapter_collision/` empty |

## Emit schema

```json
{"chosen_action": "brake", "predicted_consequence": "clear", "is_safe": true}
```

## CPU metric table — % collision correct (post-hoc GT)

Source: `data/collision_predictive/EVAL_COLLISION_CPU.json`  
Audit: `data/eval_audit/collision_20260924_050543.jsonl` (555 steps, **0** dirty prompts)

| predictor | k=1 | k=3 | k=5 | overall |
|-----------|-----|-----|-----|---------|
| **collision_physics** | **100.0** | **100.0** | **100.0** | **100.0** |
| inverse_cv (no collision) | 94.05 | 85.95 | 75.68 | 85.23 |
| collision_choose_safest | 100.0 | 100.0 | 100.0 | 100.0 |

**Ablation (collision − inverse_cv):** **+14.77 pp** overall.

### Honest interpretation

- World **is** the elastic-disk simulator → `collision_physics` matching GT at
  100% is the **CPU oracle / own-delta floor** for a future VLM (same spirit as
  inverse F1 CV pos_acc=1.0 on a CV world). **Not** a VLM claim.
- `inverse_cv` degrades with horizon (94→76%) — vision-style CV without
  masses/collision resolution misses action-conditional consequences.
- Positive ablation ⇒ the collision layer **does** improve inverse-style
  future/safety prediction on this domain (CPU).
- Contam inject-GT → **INVALID PASS**. physics_fail≈0 (k=5 rate 0.0054 edge).

### Contam / screens / adapter

| Check | Result |
|-------|--------|
| Contam self-test | PASS |
| Quantum `data/lora_adapter/` mtime | **2026-09-24 00:58:09** unchanged |
| GPU screens | preserved (no kill, no steal) |
| VLM / LoRA | **deferred** → `data/lora_adapter_collision/` |

## Paths

```
examples/collision_predictive/
  physics.py  generate.py  eval_harness.py  memory_bridge.py  README.md
data/collision_predictive/EVAL_COLLISION_CPU.json
docs/LOCK-COLLISION-PREDICTIVE.md
docs/COLLISION-PREDICTIVE-F1.md
```

## Wiring notes

- `WorkingMemory`: `memory_bridge.update_memory_from_collision` stores emit only
- Inverse: Fase 2 action-conditional sketch now has a runnable CPU cousin here
- Distance: `distance_note()` optional urgency band (heuristic; not GT meters)
