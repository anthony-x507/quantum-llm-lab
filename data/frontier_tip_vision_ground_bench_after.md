# BENCHMARK_CODIGO_VIVO — three pillars

**Written:** 2026-09-24 13:54:13 
**Model:** `mlx-community/Qwen3-VL-8B-Thinking-4bit`
**Adapter (READ-ONLY):** `/Users/anthony/Documents/quantum-llm-lab/data/lora_adapter`
**Base:** adapter=null

> No quantum-advantage claims. Execution errors reported honestly.

## Per-pillar table

| pillar | metric | base | adapter | Δ |
|--------|--------|------|---------|---|
| 1 Python | solve_rate | 0.000 (0/0) | 0.000 (0/0) | +0.000 |
| 2 Entanglement | label_acc | 0.000 (0/0) | 0.000 (0/0) | +0.000 |
| 2 Entanglement | energy_ok_rate | 0.000 (0/0) | 0.000 (0/0) | +0.000 |
| 2 Entanglement | compile_rate (PennyLane ran) | 0.000 (0/0) | 0.000 (0/0) | +0.000 |
| 3 Vision | accuracy | 1.000 (10/10) | 0.000 (0/0) | -1.000 |

## Notes
- Python set: `data/bench_live/PYTHON_SET.md` (N=0)
- Entanglement set: `data/bench_live/ENT_SET.md` (N=0)
- Vision set: `data/bench_live/VISION_SET.md` (N=10)
- Strip Thinking; max_tokens≥512; anti-leak prompts on ent pillar.
- Vision note: image→answer often helped more than pure code emission.

## Paths
- Mac: `data/frontier_tip_vision_ground_bench_after.md`
- Box copy: `/workspace/quantum-night/BENCHMARK_CODIGO_VIVO.md`
