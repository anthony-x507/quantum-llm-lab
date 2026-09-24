# Predictive collision layer

When predicting the future of a frame, evaluate **hypothetical actions** and
**physical consequences** with elastic collision physics (trajectories,
velocities, **masses**) — not vision-only.

**Emit schema:** `chosen_action` + `predicted_consequence` + `is_safe`

## Domain lock

Top-down **merge lane** (ego + vehicles/pedestrians). Separate from:
- street-lights video F1
- inverse corridor balls/boxes/signal
- quantum

Extends inverse-planning **Fase 2** (action-conditional) idea without forking
the street set. Wires into `WorkingMemory` via `memory_bridge.py`.

## Paths

```
examples/collision_predictive/
  physics.py          # elastic disks + hypo actions
  generate.py         # synth set → data/collision_predictive/
  eval_harness.py     # % collision correct + ablation vs inverse_cv
  memory_bridge.py    # emit → WorkingMemory (no GT)
data/collision_predictive/   # frames local; SUMMARY+EVAL tracked
data/lora_adapter_collision/ # empty — VLM deferred
data/eval_audit/collision_*.jsonl
```

## Run (CPU)

```bash
.venv/bin/python examples/collision_predictive/generate.py --n-seq 40 --seed 24092445
.venv/bin/python examples/collision_predictive/eval_harness.py --contam-self-test
```

Quantum `data/lora_adapter/` = **READ-ONLY**. No GPU steal.
