# Frontier — Mixed tip + freeze R1/R2 reinforces

**Branch:** `frontier/mixed-with-freeze-r2`  
**Base mixed:** `frontier/moe-verifier-mixed-live` @ `efc5e9d`  
**Freeze source:** `frontier/freeze-polish-bridge` @ `65e5c2b`  
**When:** 2026-09-24 10:58:29 ET · Mac-139 (`074c6626-…`)  
**Claim:** NO quantum advantage. Classical `python -I` + heuristic router only.

## LOCK

- Mixed unified overall **≥0.9667** (docs ~**0.967**). Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.

## What was ported

Router/verifier reinforces from freeze-polish-bridge, **merged** with mixed-live cues:

| Layer | Source | Notes |
|-------|--------|-------|
| `VISION_NEG_RE` | freeze R1 | Cancels vision on text-only / no-image |
| `ENT_NEG_RE` + bilingual `VISION_RE` | freeze R2 | ES observa/foto; cancel ent on "no circuit" chat |
| `vis_arith` + `look … sequence` | mixed tip | Kept — chalkboard / sequence hard-negs |
| `propose_heuristic` R1/R2 extractors | freeze | Gold-free int/len/count/sum/math/ES imprima |
| Hardneg fixtures R1+R2 | freeze | Router 18+22; python 12+20 |
| `--hardneg` CLI | freeze | `moe_dual_lane_router.py`, `moe_verifier_codigo_vivo.py` |

## Scoreboard mixed CPU (a)(b)(c)(d)

| Path | before | after |
|------|--------|-------|
| (a) baseline | 0.3000 | **0.3000** |
| (b) MoE alone | 0.6333 | **0.6333** |
| (c) verifier-on-python | 0.6333 | **0.6333** |
| (d) unified | **0.9667** | **0.9667** (held) |

Δ MoE vs baseline overall **+0.3333**, `moe_delta_visible=true`.  
Router pillars **26/26**, embedded mixed hardneg **10/10**.

## Hardneg R1 / R2

| Surface | R1 | R2 |
|---------|----|----|
| Router | **18/18 (1.0)** | **22/22 (1.0)** |
| Python verifier/unified loop | **1.0** (12/12) | **1.0** (20/20) |
| `ent_never_on_python` | true | true |
| `prompt_touches_gt` | false | false |

## CLI

```bash
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
python examples/moe_verifier_mixed_live.py --smoke
python examples/moe_verifier_mixed_live.py --cpu-eval
python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_mixed_router.json
python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r2_mixed_router.json
python examples/moe_verifier_codigo_vivo.py --hardneg-only
python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r2_python_items.json \
  --hardneg-router data/bench_live/hardneg_r2_mixed_router.json
```

## Artifacts

- `data/freeze_metrics/mixed_with_freeze_r2_20260924.json`
- `data/frontier_moe_verifier_mixed_cpu.json`
- `data/frontier_moe_verifier_mixed_unified.json`
- `data/frontier_moe_verifier_mixed_smoke.json`
- `data/frontier_moe_dual_lane_hardneg.json`
- `data/frontier_moe_dual_lane_hardneg_r2.json`
- `data/frontier_moe_verifier_hardneg.json`
- `data/frontier_moe_verifier_hardneg_r2.json`
- `docs/FRONTIER-FREEZE-POLISH-BRIDGE.md` (upstream freeze narrative)
- `docs/FRONTIER-MIXED-WITH-FREEZE-R2.md` (this file)

## What this does NOT do

- No merge to `main`.
- No writes under `data/lora_adapter/`.
- No quantum-advantage marketing.
- Does not pull circuit-graph scaffold (separate branch `frontier/mixed-with-scaffold`).
