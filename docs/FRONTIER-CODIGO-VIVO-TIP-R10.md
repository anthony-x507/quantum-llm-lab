# Frontier — Código-vivo tip hardneg R10

**Branch:** `frontier/tip-hardneg-r10` (side; not folded)  
**Base tip:** `3d05cbe` (post collision-n tip freeze pin / tip-vision-delta)  
**When:** 2026-09-24 ~1:35–1:45 ET · Mac-111 (`074c6626-…`)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r10`  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`. No CloudAgent.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.
- R1 / R2 / R3 / R4 / R5 / R6 / R7 / R8 / R9 / label-protect fixtures must still hold after R10 reinforce.
- Do **not** touch tip-cv (`/Users/anthony/Documents/quantum-llm-lab-tip-cv`), tip-hardneg-r9, tip-motion-r3, tip-vision-delta.

## R10 families (≠ R1–R9 / ≠ label-protect)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r10_mixed_router.json` | **52** | asyncapi_channel_gates, nomad_job_gates, vault_policy_gates, istio_virtualservice_gates, argocd_sync_gates, tekton_param_gates, flatbuffers_table_gates, capnp_struct_gates, solidity_modifier_gates, rust_cfg_feature_gates, kotlin_annotation_qubit, csproj_property_gates, sparql_bind_gates, cypher_property_gates, earthfile_target_gates + ent/vision/base controls |
| `data/bench_live/hardneg_r10_python_items.json` | **44** | same coding themes; GT stdout harness-only |

HARD traps (pre-reinforce drops): AsyncAPI `gates: subscribe`; Istio `gates: mesh`; ArgoCD `gates: Create`; Tekton `gates:`; FlatBuffers `gates: string`; Cypher `{gates:`; Earthfile target `gates:`; base chat with those distractors + ENT_NEG.

## Scores

| Surface | Pre-reinforce | Post-reinforce (1 layer) |
|---------|---------------|---------------------------|
| R10 router | 38/52 (**0.7308**) | **52/52 (1.0)** |
| R10 verifier alone loop | **1.0** (44/44) | **1.0** (44/44) |
| R10 unified loop | **1.0** (44/44) | **1.0** (44/44) |
| Mixed (d) unified overall | **1.0 (held ≥0.967)** | **1.0 (held)** |
| R1–R9 routers | held | **18/18 · 22/22 · 35/35 · 40/40 · 44/44 · 48/48 · 52/52 · 52/52 · 52/52** |
| R3–R9 verifiers | held | **28/28 · 32/32 · 36/36 · 40/40 · 44/44 · 44/44 · 44/44** |
| LP router/verifier | held | **43/43 · 32/32** |
| Router smoke | 12/12 | 12/12 |
| `ent_never_on_python` | true | true |

## Reinforce layer (gold-free, once)

1. **Router** — exclude AsyncAPI channel `gates:` / `gates: subscribe`; Istio `gates: mesh` / VirtualService; ArgoCD `gates: Create` / syncOptions; Tekton Task/Pipeline param `gates:`; FlatBuffers `gates: string` / table field; Cypher `{gates:`; Earthfile target `gates:`; messaging/CI/schema/mention prose. R1–R9 patterns unchanged.
2. **Proposer** — none (all 44 heuristic-solvable).

## Freeze polish_r10

| Manifest | pct |
|----------|-----|
| `data/freeze_manifests/tip_moe_verifier_polish_r10_100pct_*.json` | **100** |

Evidence: `data/freeze_metrics/codigo_vivo_tip_adv_r10_20260924.json`

## CLI

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r10
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r10_mixed_router.json
.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r10_python_items.json \
  --hardneg-router data/bench_live/hardneg_r10_mixed_router.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `data/bench_live/hardneg_r10_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r10.json`
- `data/frontier_moe_verifier_hardneg_r10.json`
- `data/frontier_moe_verifier_mixed_{cpu,unified}.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r10_20260924.json`
- `data/freeze_manifests/tip_moe_verifier_polish_r10_100pct_*.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R10.md` (this file)

## Not folded

Leave tip-cv / hardneg-r9 / motion-r3 / vision-delta alone until a fold brief. Side branch only.
