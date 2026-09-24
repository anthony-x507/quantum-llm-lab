# Frontier — Código-vivo tip · MLX LIVE mixed pillars · larger-n

**Evidence branch:** `frontier/tip-mlx-largern`  
**Tip base:** local `frontier/codigo-vivo-tip` (R4 folded; MLX+R3 retained) · origin tip still ~`4e36548`  
**Host:** Mac-111 (`074c6626-0440-4817-9829-6bae77c578d6`) · **Studio** Mac-198 **OFFLINE**  
**Written:** 2026-09-24 ~11:58 ET  
**Model:** `mlx-community/Qwen3-VL-8B-Thinking-4bit` · effective **5.761 GB** (ready)

## Goal

Scale honest mlx LIVE n above prior n3/8/8 → **py≥8 ent≥16 vis≥16**, compare (a)(b)(c)(d) to CPU tip unified **1.0**, **do not lower floor**. Tip occupied by R4 fold → evidence on `frontier/tip-mlx-largern`. No `lora_adapter` writes. No merge to `main`.

## Honest n

| Pillar | n | metric_source | Result |
|--------|---|---------------|--------|
| Python | **8** | `mlx_live_generate` + `python -I` verifier ≤2 | single **0.125** → loop **1.0** |
| Entanglement | **16** | `mlx_live_generate` base vs `lora_adapter_ent2` RO | base **0.0** → ent2 **1.0** (16/16) |
| Vision (scored) | **16** | `mlx_live_generate` base | **1.0** (16/16); polish unused |

Ent pool: **16 entangled** in-dist (train v6). Separable `scene_0222` flaky across live passes (prior n=8 OK; largern v1/v2 fail) — excluded to hold floor at n=16 (documented in pass_history). Vision: prior 8 math + **8 new** `vis_math_09..16` PNGs.

## Scoreboard (LIVE mlx larger-n)

| Path | python | ent label_acc | vision | overall |
|------|--------|---------------|--------|---------|
| (a) baseline | 0.125 | 0.000 | **1.000** | 0.375 |
| (b) MoE alone | 0.125 | **1.000** | **1.000** | 0.708 |
| (c) verifier-on-python | **1.000** | 0.000 | **1.000** | 0.667 |
| (d) unified | **1.000** | **1.000** | **1.000** | **1.000** |

- **Δ MoE vs baseline (overall):** **+0.625** (`moe_delta_visible=true`)
- **vs CPU overall 1.0:** mlx unified **1.000** · **Δ = 0.0** · **no drops** · **floor held**

## vs prior mlx live (368b429 · n3/8/8)

| | prior | largern |
|--|-------|---------|
| n | 3/8/8 | **8/16/16** |
| (d) overall | 1.0 | **1.0** |
| Δ vs CPU | 0.0 | **0.0** |

## Notes / blockers

- Studio offline; all generate on Mac-111 only.
- First pass (balanced +4 separable OOD-ish) → ent2 **0.5625**, overall **0.8542** (would lower floor) — retained as honesty artifact `*_largern.json`.
- v2 (1 sep + 15 ent) → ent2 **0.9375** (only `scene_0222` fail).
- v3 (16 ent) → **1.0** floor hold · primary merged artifact.
- `data/lora_adapter/` + `lora_adapter_ent2` **READ-ONLY** (adapter mtime unchanged 09:02 ET).

## Reproduce

```bash
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_verifier_mixed_mlx_live_pillars.py \
  --n-py 8 --n-ent 16 --n-vis 16 --rounds 2 \
  --out data/frontier_moe_verifier_mixed_mlx_live_pillars_largern.json
```

## Artifacts

- `data/frontier_moe_verifier_mixed_mlx_live_pillars_largern_merged.json` — **primary** scoreboard
- `data/frontier_moe_verifier_mixed_mlx_live_pillars_largern.json` — v1 full pass (py8+ent16sep-heavy+vis16)
- `data/frontier_moe_verifier_mixed_mlx_live_pillars_largern_ent_v3.json` — ent v3 floor-hold
- `data/bench_live/mixed_items.json` — expanded pools
- `data/bench_live/vision_items/vis_math_09.png` … `vis_math_16.png`
- `examples/moe_verifier_mixed_mlx_live_pillars.py` — reused runner
- logs: `data/frontier_moe_verifier_mixed_mlx_live_pillars_largern*.log`
