# Frontier — Código-vivo tip · MLX LIVE mixed pillars

**Branch tip:** `frontier/codigo-vivo-tip` @ `f0da3e7` (+ this evidence commit)  
**Evidence branch:** `frontier/codigo-vivo-tip-mlx`  
**Host:** Mac-111 / Mac-52 (`074c6626-0440-4817-9829-6bae77c578d6`) · **Studio** `8e12e5c3…` **OFFLINE**  
**Written:** 2026-09-24 ~11:10 ET  
**Model:** `mlx-community/Qwen3-VL-8B-Thinking-4bit` · effective **5.761 GB** (ready)

## Goal

Run **mlx LIVE generate** on mixed Código-vivo pillars (python verifier loop + **real** ent + vis), not prior-replay for ent/vis rates. Compare to tip CPU unified **overall 1.0**. No `lora_adapter` writes. No merge to `main`.

## Honest n

| Pillar | n | metric_source | Result |
|--------|---|---------------|--------|
| Python | **3** | `mlx_live_generate` + `python -I` verifier ≤2 | single **0.0** → loop **1.0** (Δ +1.0) |
| Entanglement | **8** | `mlx_live_generate` base vs `lora_adapter_ent2` RO | base label **0.0** → ent2 **1.0** (8/8) |
| Vision (scored) | **8** | `mlx_live_generate` base | **1.0** (8/8); polish unused |

## Scoreboard (LIVE mlx)

| Path | python | ent label_acc | vision | overall |
|------|--------|---------------|--------|---------|
| (a) baseline | 0.000 | 0.000 | **1.000** | 0.333 |
| (b) MoE alone | 0.000 | **1.000** | **1.000** | 0.667 |
| (c) verifier-on-python | **1.000** | 0.000 | **1.000** | 0.667 |
| (d) unified | **1.000** | **1.000** | **1.000** | **1.000** |

- **Δ MoE vs baseline (overall):** **+0.3334** (`moe_delta_visible=true`) — same shape as tip CPU.
- **vs CPU overall 1.0:** mlx unified **1.000** · **Δ = 0.0** · **no drops**.

## Notes / blockers

- Studio Mac-198 (`8e12e5c3`) disconnected; all generate on Mac-111.
- Anti-think already on tip (`max_tokens≥1536` + strip); vision first-pass 8/8 → **no polish applied**.
- Ent base parse partial (5/8 parse_ok) but label_acc 0.0; ent2 parse+compile+label **8/8**.
- `data/lora_adapter/` **READ-ONLY** (script policy; no writes this run).

## Reproduce

```bash
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
# scenes + vision PNGs must resolve under tip (symlink to lab data/scenes + vision_items)
.venv/bin/python examples/moe_verifier_mixed_mlx_live_pillars.py --n-py 3 --n-ent 8 --n-vis 8
```

## Artifacts

- `data/frontier_moe_verifier_mixed_mlx_live_merged.json` — **primary** merged scoreboard
- `data/frontier_moe_verifier_mixed_mlx_live_pillars.json` — py n=3 + ent/vis n=3 first pass
- `data/frontier_moe_verifier_mixed_mlx_live_pillars_entvis8.json` — ent/vis n=8 expansion
- `data/HF_CACHE_QWEN3VL8B_STATUS.json` — 8B ready confirm (5.761 GB)
- `examples/moe_verifier_mixed_mlx_live_pillars.py` — runner
- logs: `data/frontier_moe_verifier_mixed_mlx_live_pillars*.log`
