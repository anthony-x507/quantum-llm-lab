# LOCK — Inverse planning / future prediction (Anthony ~04:43 ET 2026-09-24)

**Separate domain** — do not mix with street-lights F1 or quantum until this has its **own numbers**.
Quantum `data/lora_adapter/` = READ-ONLY. No quantum-advantage claims.
Anti-contamination: future-frame GT **never** visible during prediction (post-hoc only).

## Task
At frame N, predict state at N+k (object positions, light, pedestrian) given optional hypothetical action.
GT = real frame N+k.

## Metrics
- % prediction correct (objects in expected position ± tolerance)
- Breakdown by horizon k = 1, 3, 5
- **Physics-law gate:** parabolic / spin / collision must hold; “car flies” = fail even if position luckily matches

## Evolution
1. Fase 1 — passive prediction (no action)
2. Fase 2 — prediction conditional on a model action
3. Fase 3 — model chooses action to maximize correct prediction (planning)

## Paths
- Scenes: `data/inverse_planning/`
- Adapter (later): `data/lora_adapter_inverse/`
- Never reuse video_f1 or classical adapters for this domain’s reported numbers
