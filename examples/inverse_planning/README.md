# Inverse planning domain (separate)

**Do not mix** with street-lights video F1, classical scenes, or quantum adapters/GT.

Fase 1 (passive, no action):
- `generate_passive.py` → `data/inverse_planning/` (top-down corridor balls/boxes + one signal)
- `physics.py` — kinematics gate (teleport / wall-phase → physics_fail)
- `eval_passive.py` — CV baseline first; VLM when GPU free → `data/lora_adapter_inverse/`

GT futures live only in `*_gt.json` / `futures_gt.json` sidecars, loaded post-hoc by eval.
See `docs/LOCK-INVERSE-PLANNING.md` and `docs/INVERSE-PLANNING-F1.md`.
