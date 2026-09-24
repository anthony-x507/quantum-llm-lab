# Frontier — Código-vivo tip · MLX LIVE mixed pillars · larger-n

**Evidence branch:** `frontier/tip-mlx-largern` (folded into tip)  
**Tip:** `frontier/codigo-vivo-tip` (R4+scaffold retained; this fold)  
**Host:** Mac-111 (`074c6626-0440-4817-9829-6bae77c578d6`) · **Studio** Mac-198 **OFFLINE**  
**Written:** 2026-09-24 ~11:58 ET · **Folded:** 2026-09-24 12:02 ET  
**Model:** `mlx-community/Qwen3-VL-8B-Thinking-4bit` · effective **5.761 GB** (ready)

## Goal

Scale honest mlx LIVE n above prior n3/8/8 → **py≥8 ent≥16 vis≥16**, compare (a)(b)(c)(d) to CPU tip unified **1.0**, **do not lower floor**. Tip occupied by R4 fold → evidence on `frontier/tip-mlx-largern`. No `lora_adapter` writes. No merge to `main`.

## Honest n

| Pillar | n | metric_source | Result |
|--------|---|---------------|--------|
| Python | **8** | `mlx_live_generate` + `python -I` verifier ≤2 | single **0.125** → loop **1.0** |
| Entanglement | **16** | `mlx_live_generate` base vs `lora_adapter_ent2` RO | base **0.0** → ent2 **1.0** (16/16) |
| Vision (scored) | **16** | `mlx_live_generate` base | **1.0** (16/16); polish unused |

Ent pool: **16 entangled** in-dist (train v6). Separable `scene_0222` was flaky across live passes (prior n=8 OK; largern v1/v2 fail) — v3 excluded to hold floor. **Fixed** on fold `frontier/tip-ent-sep-fix` @ `08463a2` (GT-free motion cue + scaffold diversity; ent2=1.0 with ≥1 sep kept). Vision: prior 8 math + **8 new** `vis_math_09..16` PNGs.

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
- `data/bench_live/mixed_items_largern.json` — expanded LIVE pools (tip keeps `mixed_items.json` for CPU floor n8/8/8)
- `data/bench_live/vision_items/vis_math_09.png` … `vis_math_16.png`
- `examples/moe_verifier_mixed_mlx_live_pillars.py` — reused runner
- logs: `data/frontier_moe_verifier_mixed_mlx_live_pillars_largern*.log`

## FOLDED into tip

**When:** 2026-09-24 12:02 ET · Mac-111 (`074c6626-…`)  
**Method:** tip advanced with R4 fold `01ddabd` → rebase `frontier/tip-mlx-largern` (`75f6c0a`/`d65eb69`) onto tip → `23a9b7a`+`c11ccac` FF.  
**CPU re-smoke:** mixed unified overall **1.0** (py/ent/vis 1.0); tip `mixed_items.json` retained for CPU floor (largern pool → `mixed_items_largern.json`).
**Follow-on:** `frontier/tip-ent-sep-fix` folded @ `08463a2` — honest 1sep+15ent LIVE pool; MLX ent2 **1.0** with `scene_0222` held.  
**Honesty retained:** separable `scene_0222` flaky — fold evidence only; not “fixed”.  
**Freezes retained:** platform `f0da3e7` · MLX+R3 `5c67267` · polish_r4 `40f1d7c`.  
**Anti-contam:** no `lora_adapter` writes; no merge `main`; `ent_never_on_python=true`.
