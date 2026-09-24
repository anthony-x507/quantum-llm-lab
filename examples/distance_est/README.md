# Distance estimation (FLOOR-SCALE) — temporal vision

**Scale lock (Anthony):** building floors ≈ 8–10 ft (**2.4–3.0 m**).  
**NO fixed object heights** — traffic lights are **not** a fixed 3 m (real ~3–5 m).  
Derive light/sign height by how many floors it spans in-frame, then meters to
**cars, intersections, stop signs, people** (priority), and the light itself.

Signals: **floor-scale + frame-to-frame parallax** (growing→approach, shrinking→recede).

- Data: `data/video_synth/distance_est/` (extends video_synth temporal family)
- Adapter (later): `data/lora_adapter_distance/` only — never `data/lora_adapter/`
- Separate from `data/inverse_planning/` corridor domain
- GT: `distances_gt.json` sidecars only; never in prompts

```bash
.venv/bin/python examples/distance_est/generate.py --n-seq 56
.venv/bin/python examples/distance_est/eval_heuristic.py
.venv/bin/python examples/distance_est/eval_heuristic.py --contam-self-test
```

## DANGER ZONE reinforce (30–70 m)

```bash
python examples/distance_est/generate_danger50.py --n-seq 88
python examples/distance_est/eval_heuristic.py --data data/video_synth/distance_est/danger50 --out-name EVAL_DANGER50_CPU.json
```

Soft priors: car ~4.5 m length, ped ~1.7 m height. Lights: floor-span only (no fixed height). Closing-speed / TTI from apparent growth.

