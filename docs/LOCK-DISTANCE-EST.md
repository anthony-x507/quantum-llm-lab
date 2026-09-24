# LOCK — Distance estimation (FLOOR-SCALE) (Anthony ~04:50 ET 2026-09-24)

**Scale = BUILDING FLOORS**, not fixed object heights.

1. Each building floor ≈ **8–10 ft (2.4–3.0 m)**, standard.
2. **NO fixed object heights.** Traffic lights are **not** 3 m fixed (real range ~3–5 m by intersection). Derive light/sign height by **how many floors it spans** in the frame.
3. Priority distances: **cars, intersections, stop signs, people motion** — object height is a means, not the goal.
4. Signals: **floor-calibrated scale + frame-to-frame parallax** to triangulate (growing→approach, shrinking→recede).
5. GT = known 3D positions in **synthetic render sidecars only**; **never** in inference prompts / memory / retrieval.
6. Metric: % correct distance by range band (tol 10% if GT&lt;50 m, 20% if 50–200 m) **and** whether floor-calibrated distance improves **tracking** and **future/depth prediction** vs tracking-only.
7. Quantum `data/lora_adapter/` = **READ-ONLY**. New adapters → `data/lora_adapter_distance/` only.
8. Do **not** mix with inverse_planning corridor geometry (may compare prediction ablation only).
9. Do **not** kill GPU screens; share via `data/TRAIN_LOCK.txt`; queue behind existing waiters.
10. No quantum-advantage claims. No external Gemini/GPT benches.

See `docs/DISTANCE-EST-F1.md`.
