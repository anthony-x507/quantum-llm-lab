# Inverse planning domain (separate)

**Do not mix** with street-lights video F1, classical scenes, or quantum adapters/GT.

Fase 1 (passive, no action):
- `generate_passive.py` → `data/inverse_planning/` (top-down corridor balls/boxes + one signal)
- `physics.py` — kinematics gate (teleport / wall-phase → physics_fail)
- `eval_passive.py` — CV baseline first; VLM when GPU free → `data/lora_adapter_inverse/`

GT futures live only in `*_gt.json` / `futures_gt.json` sidecars, loaded post-hoc by eval.
See `docs/LOCK-INVERSE-PLANNING.md` and `docs/INVERSE-PLANNING-F1.md`.

## Related — predictive collision (Fase 2 cousin)

Action-conditional collision consequences (CPU): `examples/collision_predictive/` — does **not** replace this corridor domain; ablation compares collision layer vs inverse-style CV on its own merge-lane set.
