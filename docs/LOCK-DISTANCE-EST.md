# LOCK — Distance estimation (FLOOR-SCALE) (Anthony ~04:50 ET 2026-09-24; danger50 ~05:12 ET)

**Scale = BUILDING FLOORS**, not fixed object heights.

1. Each building floor ≈ **8–10 ft (2.4–3.0 m)**, standard.
2. **NO fixed traffic-light heights.** Lights vary ~3–5 m by intersection. Derive light/sign height by **floor-span** in frame.
3. Soft apparent-size priors **only** for cars (~4.5 m length) and pedestrians (~1.7 m height) — triangulate with floor-scale + ground-plane. **Not** for lights.
4. Priority distances: **cars, intersections, stop signs, people motion** — object height is a means, not the goal.
5. Signals: **floor-calibrated scale + fine frame-to-frame parallax + closing-speed/TTI** (growth % → v_close → time-to-impact).
6. **DANGER ZONE 30–70 m** is the reinforce target (baseline ~50 m band was weakest).
7. GT = known 3D positions in **synthetic render sidecars only**; **never** in inference prompts / memory / retrieval.
8. Metric: % correct by band **and** % correct in 30–70 m; ablation tracking / inverse-style future-pred **in danger zone**.
9. Quantum `data/lora_adapter/` = **READ-ONLY**. New adapters → `data/lora_adapter_distance/` only.
10. Do **not** mix with inverse_planning corridor geometry (may compare prediction ablation only).
11. Do **not** kill GPU screens; share via `data/TRAIN_LOCK.txt`; queue behind existing waiters.
12. No quantum-advantage claims. No external Gemini/GPT benches.

See `docs/DISTANCE-EST-F1.md`.
