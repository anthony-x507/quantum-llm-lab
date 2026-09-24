# BENCHMARK_CLASSICAL

Written: 2026-09-24 04:34:50 ET

Lane: **classical visual physics** (NOT quantum). No quantum-advantage claims.

## Goal
Image → executable Python → numeric `{range_m, max_height_m, impact_speed_m_s}` within tolerance.

## Dataset
- Path: `data/classical_scenes/`
- N = **220** (seed 240924), gold_python verified **220/220**
- Subdomains (~27–28 each): baseball, soccer, golf, ballistic,
  angled_projectile, drag_projectile, elastic_collision, inelastic_collision
- Docs: `data/classical_scenes/SUMMARY.md`, `CLASSICAL_SET.md`

## Gold Python sanity (CPU harness)
- n=220 exec_rate=**1.000** match_rate=**1.000**
- Breakdown:
  - `angled_projectile`: n=27 match=1.00
  - `ballistic`: n=28 match=1.00
  - `baseball`: n=28 match=1.00
  - `drag_projectile`: n=27 match=1.00
  - `elastic_collision`: n=27 match=1.00
  - `golf`: n=28 match=1.00
  - `inelastic_collision`: n=27 match=1.00
  - `soccer`: n=28 match=1.00

## Train status
- Target adapter: `data/lora_adapter_classical/` (SEPARATE from quantum `data/lora_adapter/` READ-ONLY).
- Dataset JSONL: `data/lora_dataset_classical.jsonl` (220 rows, anti-leak suspicious=0).
- GPU held by `qlora-ent` at build time → prepare-only DONE; smoke 1ep queued in screen `qlora-classical`.

## Transfer vs quantum adapter
- When GPU free: eval quantum `data/lora_adapter/` READ-ONLY on classical set.
- Expect **poor transfer** (circuit JSON ≠ classical Python). Report honestly.

## Scripts
- `examples/synthetic_classical_physics.py`
- `examples/train_lora_classical.py`
- `examples/eval_classical.py`

## Live VLM rows
- `classical_lora`: pending smoke/full train
- `base`: pending
- `quantum_transfer_readonly`: pending

