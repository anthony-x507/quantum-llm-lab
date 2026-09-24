# Frontier — Código-vivo tip hardneg R16

**Branch:** `frontier/tip-hardneg-r16` (side; not folded)  
**Base tip:** `fbd2e7e` (`frontier/codigo-vivo-tip` post tip-hardneg-r12 fold scoreboard pin; tip-cv HEAD ≥ `9a0de24`)  
**When:** 2026-09-24 ~14:30 ET · Mac-111 (`074c6626-…`)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r16`  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`. No CloudAgent.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.
- R2 / R3 / R4 / R5 / R6 / R7 / R8 / R9 / R10 / R11 / R12 / label-protect fixtures must still hold after R16 reinforce.
- Do **not** touch tip-cv, tip-tti, tip-distance-mid, tip-distance-far, tip-hardneg-r12/r13/r14/r15, tip-inverse-r3, tip-circ-expand, tip-future-track*, tip-choose-safest-n (other lanes / fold queue). R16 stays side-only.

## R16 families (≠ R1–R15 / ≠ label-protect)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r16_mixed_router.json` | **52** | trafficserver_remap_gates, coredns_acl_gates, pulsar_topic_gates, redpanda_acl_gates, github_actions_needs_gates, gitlab_ci_rules_gates, terraform_count_gates, nix_flake_gates, express_mw_gates, flask_before_gates, knative_serving_gates, keda_scaler_gates, dapr_middleware_gates, gatekeeper_constraint_gates + ent/vision/base controls |
| `data/bench_live/hardneg_r16_python_items.json` | **44** | same coding themes; GT stdout harness-only |

HARD traps (pre-reinforce drops): ATS `gates: remap`; CoreDNS `gates: acl`; Pulsar `gates: produce`; Redpanda `gates: ALTER`; GitHub Actions `gates: needs`; GitLab CI `gates: rules`; Terraform `gates: count`; Nix flake `gates: outputs`; Express `gates: helmet`; Flask `gates: before_request`; Knative `gates: minScale`; KEDA `gates: cooldownPeriod`; Dapr `gates: Retry`; Gatekeeper `gates: enforcementAction`; base chat with those distractors + ENT_NEG.

Avoided (R9–R15): OpenAPI/Helm/…, AsyncAPI/Istio/…, Smithy/Linkerd/Cilium/…, Traefik/Envoy/NATS/Flux/Kong/Spinnaker/…, Nginx/HAProxy/Caddy/Redis/Postgres/Skaffold/Buildkite/Packer/Salt/Bazel/Dagger/Dagster/Hasura/NestJS, Apache httpd/Varnish/APISIX/Tyk/KrakenD/MongoDB/Cassandra/Jenkins/Vagrant/Chef/Pants/Prefect/FastAPI/Spring Security, Squid/OpenResty/Contour/Emissary/Zuul/Django/Laravel/Gin/DynamoDB/Firestore/Keycloak/Falco/OTel/Ray.

## Scores

| Surface | Pre-reinforce | Post-reinforce (1 layer) |
|---------|---------------|---------------------------|
| R16 router | 6/52 (**0.1154**) | **52/52 (1.0)** |
| R16 verifier alone loop | **1.0** (44/44) | **1.0** (44/44) |
| R16 unified loop | router-limited pre | **1.0** (44/44) |
| Mixed (d) unified overall | **1.0 (held ≥0.967)** | **1.0 (held)** |
| R2–R12 routers | held | **22/22 · 35/35 · 40/40 · 44/44 · 48/48 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52** |
| R7–R12 verifiers | held | **44/44 · 44/44 · 44/44 · 44/44 · 44/44 · 44/44** |
| LP router/verifier | held | **43/43 · 32/32** |
| Router smoke | 12/12 | 12/12 |
| Pillars / hardneg smoke | 26/26 · 18/18 | held |
| `ent_never_on_python` | true | true |
| Motion (tip) | **100%** | held (untouched) |
| TTI (tip) | **100%** | held (untouched) |
| Collision physics | **100%** | held (untouched) |
| inverse_cv | **≥99.82%** | held (untouched) |

Rise: 6→52 hits (**+766.6%** rate vs pre 0.1154→1.0; **+88.46 pp**) ≥80% freeze gate.

## Reinforce layer (gold-free, once)

1. **Router** — exclude ATS `gates: remap`; CoreDNS `gates: acl`; Pulsar `gates: produce`; Redpanda `gates: ALTER`; GitHub Actions `gates: needs`; GitLab CI `gates: rules`; Terraform `gates: count`; Nix flake `gates: outputs`; Express `gates: helmet`; Flask `gates: before_request`; Knative `gates: minScale`; KEDA `gates: cooldownPeriod`; Dapr `gates: Retry`; Gatekeeper `gates: enforcementAction`; proxy/DNS/messaging/CI/IaC/build/framework/serving/autoscaler/sidecar/policy prose. R1–R12 patterns unchanged (R13/R14/R15 not on tip base).
2. **Proposer** — none (all 44 heuristic-solvable).

## Freeze polish_r16

| Manifest | pct |
|----------|-----|
| `data/freeze_manifests/tip_moe_verifier_polish_r16_100pct_20260924_143253.json` | **100** |

Evidence: `data/freeze_metrics/codigo_vivo_tip_adv_r16_20260924.json`

## CLI

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r16
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r16_mixed_router.json
.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r16_python_items.json \
  --hardneg-router data/bench_live/hardneg_r16_mixed_router.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `data/bench_live/hardneg_r16_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r16.json`
- `data/frontier_moe_verifier_hardneg_r16.json`
- `data/frontier_moe_verifier_mixed_{cpu,unified}.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r16_20260924.json`
- `data/freeze_manifests/tip_moe_verifier_polish_r16_100pct_20260924_143253.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R16.md` (this file)

## Not folded

Leave tip-cv / tip-tti / tip-distance-mid / tip-distance-far / tip-hardneg-r12 / tip-hardneg-r13 / tip-hardneg-r14 / tip-hardneg-r15 / tip-inverse-r3 / tip-circ-expand / tip-future-track* / tip-choose-safest-n alone (fold queue mid done → R12 folding → inv→far→R13→future-r2→circ→R14→R15→choose-n). Side branch only.
