# Frontier — Código-vivo tip · ent separable fix (n=16)

**Evidence branch:** `frontier/tip-ent-sep-fix`  
**Tip base:** `c11ccac` (codigo-vivo-tip HEAD with largern folded; tip may be fold-busy → separate branch)  
**Host:** Mac-111 (`074c6626-0440-4817-9829-6bae77c578d6`)  
**Written:** 2026-09-24 ~12:21 ET  
**Model:** `mlx-community/Qwen3-VL-8B-Thinking-4bit` · effective **5.761 GB**

## Goal

Reinforce MoE / fixtures so **separable at n=16 does not drop ent2**. Prior largern honesty:

| pass | pool | ent2 | note |
|------|------|------|------|
| v1 | sep-heavy | 0.5625 | floor drop |
| v2 | 1 sep (`scene_0222`) + 15 ent | **0.9375** | only `scene_0222` fail |
| v3 | 16 ent (sep dropped) | **1.0** | floor hold, **not honest mixed** |

Target: ent2 ≥ 0.9375 prefer **1.0** on mixed set that **includes ≥1 separable**, unified overall ≥ 0.967 prefer 1.0. **No fake 1.0 by dropping hard cases.**

## Fix (GT-free)

1. **Scaffold prior diversity** — default alphabetical top-k was Bell-only; now always surfaces product + Bell when cue-weak; cue-strong skips opposite-family injection.
2. **`scaffold_polish=True`** on live ent MoE path.
3. **GT-free visual motion cue** — RGB color-centroid velocity correlation from frames (never reads `meta.entangled` / label). `independent` → product-state priors; `correlated` → Bell priors.
4. **Fixtures** — restore `scene_0222` (separable) + 15 entangled in `data/bench_live/mixed_items.json`.

No `lora_adapter` writes. No merge to `main`.

## Scoreboard (LIVE)

| Path | python | ent label_acc | vision | overall |
|------|--------|---------------|--------|---------|
| (a) baseline | 0.125† | 0.000 | 1.000† | 0.375 |
| (b) MoE alone | 0.125† | **1.000** | 1.000† | 0.708 |
| (c) verifier-on-python | 1.000† | 0.000 | 1.000† | 0.667 |
| (d) unified | **1.000†** | **1.000** | **1.000†** | **1.000** |

† python + vision rates reused from largern merged live (same host/model); **ent re-run live this branch**.

- **ent2 with ≥1 separable:** **1.0** (16/16) — `scene_0222` → gates `h,h` / label `separable`
- **vs CPU overall 1.0:** Δ = 0.0 · **floor held**
- **Hard case kept:** `scene_0222` present (not dropped as in v3)

## Reproduce

```bash
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_verifier_mixed_mlx_live_pillars.py \
  --n-py 8 --n-ent 16 --n-vis 16 --rounds 2 --skip-py --skip-vis \
  --out data/frontier_moe_verifier_mixed_mlx_live_pillars_ent_sep_fix.json
# After fold: LIVE pool is data/bench_live/mixed_items_largern.json (1 sep + 15 ent)
```

## Artifacts

- `data/frontier_moe_verifier_mixed_mlx_live_pillars_ent_sep_fix_merged.json` — primary scoreboard
- `data/frontier_moe_verifier_mixed_mlx_live_pillars_ent_sep_fix.json` — live ent run
- `data/probe_scene_0222_ent_sep_fix.json` — micro probe
- `data/bench_live/mixed_items.json` — 1 sep + 15 ent
- `examples/circuit_graph_moe_scaffold.py` — diversity + motion cue
- `examples/bench_codigo_vivo.py` — cue wire into ent pillar
- `examples/moe_verifier_mixed_mlx_live_pillars.py` — polish on

## Blockers

- Studio Mac-198 offline; all generate on Mac-111.
- Motion cue is color-tint centroid heuristic — fails open (`unknown`) on many scenes (keeps balanced priors); sufficient to recover `scene_0222`.

## FOLDED into tip

**When:** 2026-09-24 12:24:30 ET · Mac-111 (`074c6626-…`)  
**Method:** rebase `47975a7` (parent `c11ccac`) onto tip `459f6da` → `08463a2` FF into `frontier/codigo-vivo-tip`.  
**Pool split (post-largern fold):** tip CPU floor stays `data/bench_live/mixed_items.json` (n=8, already includes `scene_0222`); honest LIVE 1sep+15ent → `data/bench_live/mixed_items_largern.json`. MLX runner keeps largern path + `scaffold_polish=True`.  
**CPU re-smoke:** unified overall **1.0**; hardneg R1–R4 **18/18·22/22·35/35·40/40**; R3/R4 verifier **28/28·32/32**; `wired_to_vlm=true`. Freezes retained. No `lora_adapter` writes. No `main` merge.

**Reproduce (CPU floor):**
```bash
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_verifier_mixed_live.py --smoke
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

