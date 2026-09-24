# Frontier — Codigo-vivo tip · MLX + R3 consolidate

**Branch:** `frontier/codigo-vivo-tip`  
**Freeze id:** `codigo_vivo_tip_mlx_r3_100pct_20260924_112131`  
**Frozen SHA:** `5c672671419546de7b510e793875c95e070a0e34` (`5c67267`)  
**When:** 2026-09-24 11:21:31 ET · Mac-111 (`074c6626-…`)  
**Claim:** NO quantum advantage. Classical MoE + `python -I` verifier + prior-replay ent/vis + GT-free scaffold + mlx live + hardneg R3.

## Lineage (already linear — no merge needed)

| Step | SHA | Role |
|------|-----|------|
| base platform tip | `f0da3e7` | MFV overall 1.0 + scaffold ON + R1/R2 |
| MLX live evidence | `368b429` | mlx LIVE py/ent/vis → overall **1.0** (=CPU) |
| PLATFORM freeze write | `b114c51` | lock overall 1.0 @ **f0da3e7** (never abandon) |
| hardneg R3 polish | `5c67267` | R3 35/35 + floor **1.0** held |
| this consolidate freeze | `5c67267` | cite MLX+R3; keep prior manifests |
| scaffold-wire-vlm fold | `ae62ce2` | wire→VLM on tip; **freeze retained** |

## LOCK

- Platform freeze **f0da3e7** / `codigo_vivo_tip_platform_100pct_20260924_111435` **NOT abandoned**.
- Mixed overall **≥0.9667** (docs ~0.967); prefer **1.0**. Never abandon.
- `data/lora_adapter/` **READ-ONLY**. No merge to `main`.
- `ent_never_on_python=true`, `prompt_touches_gt=false`.

## Re-smoke (this freeze)

| Check | Result |
|-------|--------|
| Smoke pillars | **26/26** |
| Smoke embedded hardneg | **18/18** |
| CPU (d) unified | **py 1.0 / ent 1.0 / vis 1.0 / overall 1.0** |
| MoE delta overall | **+0.3334** visible |
| Hardneg R1 / R2 / R3 | **18/18 · 22/22 · 35/35** |
| MLX live (d) | **1.0** (delta vs CPU **0**) |
| Floor held | **yes** (≥0.967, actual 1.0) |

## Artifacts

| Kind | Path |
|------|------|
| Manifest | `data/freeze_manifests/codigo_vivo_tip_mlx_r3_100pct_20260924_112131.json` |
| Metrics | `data/freeze_metrics/codigo_vivo_tip_mlx_r3_20260924.json` |
| Platform (retained) | `data/freeze_manifests/codigo_vivo_tip_platform_100pct_20260924_111435.json` |
| R3 polish (retained) | `data/freeze_manifests/tip_moe_verifier_polish_r3_100pct_20260924_111740.json` |
| MLX merged | `data/frontier_moe_verifier_mixed_mlx_live_merged.json` |
| Docs | `docs/FRONTIER-CODIGO-VIVO-TIP-MLX.md`, `docs/FRONTIER-CODIGO-VIVO-TIP-R3.md` |

## Reproduce

```bash
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_verifier_mixed_live.py --smoke
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
.venv/bin/python examples/moe_dual_lane_router.py --hardneg
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r2_mixed_router.json
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r3_mixed_router.json
```



## Post-freeze fold — scaffold-wire-vlm (does NOT abandon this freeze)

**When:** 2026-09-24 11:24:45 ET · Mac-111 (`074c6626-…`)  
**Tip after fold:** `ae62ce2` (rebase `8f5e694` onto consolidate `e680271` + FF)  
**This freeze SHA `5c67267` / id `codigo_vivo_tip_mlx_r3_100pct_20260924_112131`:** **RETAINED** (not abandoned).  
**Platform freeze `f0da3e7`:** **RETAINED**.

| Check | Result |
|-------|--------|
| CPU (d) unified re-smoke | **py 1.0 / ent 1.0 / vis 1.0 / overall 1.0** |
| Smoke pillars / hardneg | **26/26 · 18/18** |
| `wired_to_vlm` | **true** (`text_scaffold_prefix`) |
| scaffold Δsolve / hard | **0.5 / 0.6666**; freeze_held |
| Floor ≥0.967 | **held at 1.0** |
| `ent_never_on_python` | **true** |

Detail: `docs/FRONTIER-SCAFFOLD-WIRE-VLM.md` · scoreboard fold section.

## What this does NOT do

- No merge to `main`.
- No writes under `data/lora_adapter/`.
- No delete of prior freeze manifests.
- No quantum-advantage marketing.
