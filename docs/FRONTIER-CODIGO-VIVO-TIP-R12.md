# Frontier — Código-vivo tip hardneg R12

**Branch:** `frontier/tip-hardneg-r12` (rebased; source kept) · tip `frontier/codigo-vivo-tip`  
**Base tip:** `a27b6fd` (post tip motion-r4 freeze pin; tip had advanced past brief pin `3f5f1b1`)  
**When:** 2026-09-24 ~2:00–2:03 ET · Mac-111 (`074c6626-…`)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r12`  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`. No CloudAgent.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.
- R1 / R2 / R3 / R4 / R5 / R6 / R7 / R8 / R9 / R10 / label-protect fixtures must still hold after R12 reinforce.
- Do **not** touch tip-cv, tip-tti, tip-distance-mid, tip-motion-r4, tip-hardneg-r11 (other lanes). R11 remains a separate side; R12 does not fold R11.

## R12 families (≠ R1–R11 / ≠ label-protect)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r12_mixed_router.json` | **52** | traefik_middleware_gates, envoy_filter_gates, nats_subject_gates, clickhouse_setting_gates, dbt_model_gates, crossplane_claim_gates, flux_kustomization_gates, rabbitmq_policy_gates, elasticsearch_ingest_gates, swift_property_gates, elixir_attribute_gates, julia_macro_gates, kong_plugin_gates, spinnaker_stage_gates + ent/vision/base controls |
| `data/bench_live/hardneg_r12_python_items.json` | **44** | same coding themes; GT stdout harness-only |

HARD traps (pre-reinforce drops): Traefik `gates: stripPrefix`; Envoy `gates: HTTP`; NATS `gates: publish`; ClickHouse `gates: Readonly`; dbt `gates: ephemeral`; Crossplane `gates: Ready`; Flux `gates: prune`; RabbitMQ `gates: ha-mode`; Elasticsearch `gates: set`; Swift `gates: Wrapped`; Elixir `gates: :atom`; Julia `gates: Symbol`; Kong `gates: rate-limiting`; Spinnaker `gates: manualJudgment`; base chat with those distractors + ENT_NEG.

Avoided (R9/R10/R11): OpenAPI/Helm/Pulumi/…, AsyncAPI/Istio/ArgoCD/Tekton/…, Smithy/Linkerd/Cilium/Airflow/Kafka/Prometheus/Kyverno/Temporal/….

## Scores

| Surface | Pre-reinforce | Post-reinforce (1 layer) |
|---------|---------------|---------------------------|
| R12 router | 6/52 (**0.1154**) | **52/52 (1.0)** |
| R12 verifier alone loop | **1.0** (44/44) | **1.0** (44/44) |
| R12 unified loop | router-limited pre | **1.0** (44/44) |
| Mixed (d) unified overall | **1.0 (held ≥0.967)** | **1.0 (held)** |
| R1–R10 routers | held | **18/18 · 22/22 · 35/35 · 40/40 · 44/44 · 48/48 · 52/52 · 52/52 · 52/52 · 52/52** |
| R3–R10 verifiers | held | **28/28 · 32/32 · 36/36 · 40/40 · 44/44 · 44/44 · 44/44 · 44/44** |
| LP router/verifier | held | **43/43 · 32/32** |
| Router smoke | 12/12 | 12/12 |
| `ent_never_on_python` | true | true |
| Motion (tip / if available) | **100%** known (motion-r4 on tip) | held (untouched) |
| Collision physics | **100%** | held (untouched) |
| inverse_cv | **≥99.82%** (inverse-r2 on tip) | held (untouched) |

Rise: 6→52 hits (**+766%** rate vs pre 0.1154→1.0; **+88.46 pp**) ≥80% freeze gate.

## Reinforce layer (gold-free, once)

1. **Router** — exclude Traefik `gates: stripPrefix`; Envoy `gates: HTTP`; NATS `gates: publish`; ClickHouse `gates: Readonly`; dbt `gates: ephemeral`; Crossplane `gates: Ready`; Flux `gates: prune`; RabbitMQ `gates: ha-mode`; Elasticsearch `gates: set`; Swift `gates: Wrapped`; Elixir `gates: :atom`; Julia `gates: Symbol`; Kong `gates: rate-limiting`; Spinnaker `gates: manualJudgment`; proxy/messaging/DB/SQL/k8s/GitOps/broker/search/language/BEAM/gateway/CD prose. R1–R10 patterns unchanged (R11 not on tip base).
2. **Proposer** — none (all 44 heuristic-solvable).

## Freeze polish_r12

| Manifest | pct |
|----------|-----|
| `data/freeze_manifests/tip_moe_verifier_polish_r12_100pct_20260924_140230.json` | **100** (sha `b4a3999`) |

Evidence: `data/freeze_metrics/codigo_vivo_tip_adv_r12_20260924.json`

## CLI

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r12
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r12_mixed_router.json
.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r12_python_items.json \
  --hardneg-router data/bench_live/hardneg_r12_mixed_router.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `data/bench_live/hardneg_r12_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r12.json`
- `data/frontier_moe_verifier_hardneg_r12.json`
- `data/frontier_moe_verifier_mixed_{cpu,unified}.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r12_20260924.json`
- `data/freeze_manifests/tip_moe_verifier_polish_r12_100pct_20260924_140230.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R12.md` (this file)

## Not folded

Leave tip-cv / tip-tti / tip-distance-mid / tip-motion-r4 / tip-hardneg-r11 alone until a fold brief. Side branch only.

## Fold re-smoke (2026-09-24 14:28:30 ET)

Cherry-pick rebase `eb58bb8`/`28d658f` onto tip `9a0de24` → `b4a3999`+`6013c2a` (conflicts: mid floors kept; R11+R12 hardneg merged).

| Surface | Score |
|---------|-------|
| mixed (d) unified | **1.0** |
| R12 router · verifier | **52/52 · 44/44** |
| R11 router · verifier | **52/52 · 44/44** |
| mid / TTI / motion / inverse / collision | **retained** |
| pillars / hardneg smoke | **26/26 · 18/18** |
| Freeze | `codigo_vivo_tip_r12_100pct_20260924_142830` |
| Tip fold SHA | `db6d93e` |
| RO adapters | **unchanged mtime** |

CLI (tip-cv):

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-cv
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r12_mixed_router.json
.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r12_python_items.json \
  --hardneg-router data/bench_live/hardneg_r12_mixed_router.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

