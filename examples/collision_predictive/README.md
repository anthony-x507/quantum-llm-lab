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
Consumes floor-scale **distance estimates** via `distance_consumer.py` stubs
(no import of unmerged `tip-distance-danger` code).

## Paths

```
examples/collision_predictive/
  physics.py             # elastic disks + hypo actions
  generate.py            # synth set → data/collision_predictive/
  eval_harness.py        # % collision correct + ablation vs inverse_cv
  memory_bridge.py       # emit → WorkingMemory (no GT)
  distance_consumer.py   # stub-safe distance urgency cues (30–70 m DZ)
data/collision_predictive/   # frames local; SUMMARY+EVAL tracked
data/lora_adapter_collision/ # empty — VLM deferred
data/eval_audit/collision_*.jsonl
data/frontier_tip_collision_pred_probe.json
data/frontier_tip_collision_n_probe.json
```

## Run (CPU)

```bash
.venv/bin/python examples/collision_predictive/generate.py --n-seq 200 --n-train 160 --n-eval 40 --seed 24092446
.venv/bin/python examples/collision_predictive/eval_harness.py --contam-self-test
```

Quantum `data/lora_adapter/` = **READ-ONLY**. No GPU steal.

## n-expand defaults (tip-collision-n)

Default synth is now **200** sequences (**160** train / **40** eval), seed `24092446`.
Prior thin set was 40 / 32 / 8 @ seed `24092445`. Physics oracle held 100% at larger n.

## tip-choose-safest-n (side)

Defaults: **400 / 320 / 80**, seed **24092447**, hardneg mix for choose_safest pressure.
Eval oracle physics + choose_safest held **100%** @ **5670** queries. Do not fold.
