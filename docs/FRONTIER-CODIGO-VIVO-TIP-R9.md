# Frontier — Código-vivo tip hardneg R9

**Branch:** `frontier/tip-hardneg-r9` (side; not folded yet)  
**Base tip:** `763fb8c` (post motion-r2 tip freeze)  
**When:** 2026-09-24 ~1:25–1:30 ET · Mac-111 (`074c6626-…`)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r9`  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`. No CloudAgent.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.
- R1 / R2 / R3 / R4 / R5 / R6 / R7 / R8 / label-protect fixtures must still hold after R9 reinforce.
- Do **not** touch tip-cv (`/Users/anthony/Documents/quantum-llm-lab-tip-cv`), tip-motion-r2, tip-collision-pred, tip-distance-danger, tip-hardneg-r8.

## R9 families (≠ R1–R8 / ≠ label-protect)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r9_mixed_router.json` | **52** | openapi_path_gates, helm_values_yaml_gates, pulumi_config_gates, cloudformation_param_gates, bicep_param_gates, thrift_field_gates, avro_record_gates, go_build_tag_gates, java_anno_qubit, powershell_param_gates, latex_newcommand_gates, grpc_rpc_gates, dhall_record_gates, justfile_recipe_gates, cedar_policy_gates + ent/vision/base controls |
| `data/bench_live/hardneg_r9_python_items.json` | **44** | same coding themes; GT stdout harness-only |

HARD traps (pre-reinforce drops): Helm `gates: enabled`; Cedar `when { gates:`; Justfile recipe `gates:`; OpenAPI `/gates:`; Pulumi `gates:prod`; CFN `Gates:`; Dhall `gates : Bool`; base chat with those distractors + ENT_NEG.

## Scores

| Surface | Pre-reinforce | Post-reinforce (1 layer) |
|---------|---------------|---------------------------|
| R9 router | 34/52 (**0.6538**) | **52/52 (1.0)** |
| R9 verifier alone loop | **1.0** (44/44) | **1.0** (44/44) |
| R9 unified loop | **1.0** (44/44) | **1.0** (44/44) |
| Mixed (d) unified overall | **1.0 (held ≥0.967)** | **1.0 (held)** |
| R1–R8 routers | held | **18/18 · 22/22 · 35/35 · 40/40 · 44/44 · 48/48 · 52/52 · 52/52** |
| R3–R8 verifiers | held | **28/28 · 32/32 · 36/36 · 40/40 · 44/44 · 44/44** |
| LP router/verifier | held | **43/43 · 32/32** |
| Router smoke | 12/12 | 12/12 |
| `ent_never_on_python` | true | true |

## Reinforce layer (gold-free, once)

1. **Router** — exclude OpenAPI `/gates:`; Helm `gates: enabled|disabled` / values.yaml; Pulumi `gates:prod|tag`; CFN Parameters Gates:; Dhall `gates : Bool|Text|…`; Justfile recipe `gates:`; Cedar `when { gates:` / `gates: true|false|attr`. R1–R8 patterns unchanged.
2. **Proposer** — none (all 44 heuristic-solvable).

## Freeze polish_r9

| Manifest | pct |
|----------|-----|
| `data/freeze_manifests/tip_moe_verifier_polish_r9_100pct_*.json` | **100** |

Evidence: `data/freeze_metrics/codigo_vivo_tip_adv_r9_20260924.json`

## CLI

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r9
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r9_mixed_router.json
.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r9_python_items.json \
  --hardneg-router data/bench_live/hardneg_r9_mixed_router.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `data/bench_live/hardneg_r9_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r9.json`
- `data/frontier_moe_verifier_hardneg_r9.json`
- `data/frontier_moe_verifier_mixed_{cpu,unified}.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r9_20260924.json`
- `data/freeze_manifests/tip_moe_verifier_polish_r9_100pct_*.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R9.md` (this file)

## Not folded

Leave tip-cv / motion-r2 / collision-pred / distance-danger / hardneg-r8 alone until a fold brief. Side branch only.
