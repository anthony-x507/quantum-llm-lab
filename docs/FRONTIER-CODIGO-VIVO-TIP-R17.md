# Frontier — Código-vivo tip hardneg R17

**Branch:** `frontier/tip-hardneg-r17` (side; not folded)  
**Base tip:** `34c696f` (`frontier/codigo-vivo-tip` post tip-inverse-r3 fold freeze/doc sha pin)  
**When:** 2026-09-24 ~14:34–14:36 ET · Mac-111 (`074c6626-…`)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r17`  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`. No CloudAgent.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.
- R2 / R3 / R7 / R8 / R9 / R10 / R11 / R12 / label-protect fixtures must still hold after R17 reinforce.
- Do **not** touch tip-cv, tip-tti, tip-distance-mid/far, tip-hardneg-r12..r16, tip-inverse-r3, tip-circ-expand, tip-future-track*, tip-choose-safest-n (other lanes / fold queue). R17 stays side-only.

## R17 families (≠ R1–R16 / ≠ label-protect)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r17_mixed_router.json` | **52** | cloudflare_worker_gates, cloudfront_behavior_gates, vitess_vschema_gates, cockroach_grant_gates, pinot_table_gates, circleci_when_gates, drone_when_gates, maven_profile_gates, sbt_task_gates, rails_before_action_gates, phoenix_plug_gates, flagger_canary_gates, argorollouts_step_gates, debezium_filter_gates + ent/vision/base controls |
| `data/bench_live/hardneg_r17_python_items.json` | **44** | same coding themes; GT stdout harness-only |

HARD traps (pre-reinforce drops): Cloudflare Worker `gates: fetch`; CloudFront `gates: PathPattern`; Vitess `gates: sharded`; CockroachDB `gates: GRANT`; Pinot `gates: ingestion`; CircleCI `gates: equal`; Drone CI `gates: event`; Maven `gates: activeByDefault`; sbt `gates: dependsOn`; Rails `gates: before_action`; Phoenix `gates: plug`; Flagger `gates: stepWeight`; Argo Rollouts `gates: setWeight`; Debezium `gates: op`; base chat with those distractors + ENT_NEG.

Avoided (R9–R16): OpenAPI/Helm/…, AsyncAPI/Istio/…, Smithy/Linkerd/Cilium/…, Traefik/Envoy/NATS/Flux/Kong/Spinnaker/…, Nginx/HAProxy/Caddy/Redis/Postgres/Skaffold/Buildkite/…, Apache httpd/Varnish/APISIX/Tyk/…, Squid/OpenResty/Contour/Emissary/Zuul/Django/Laravel/Gin/…, ATS/CoreDNS/Pulsar/Redpanda/GHA/GitLab/Terraform/Nix/Express/Flask/Knative/KEDA/Dapr/Gatekeeper.

## Scores

| Surface | Pre-reinforce | Post-reinforce (1 layer) |
|---------|---------------|---------------------------|
| R17 router | 8/52 (**0.1538**) | **52/52 (1.0)** |
| R17 verifier alone loop | **1.0** (44/44) | **1.0** (44/44) |
| R17 unified loop | router-limited pre | **1.0** (44/44) |
| Mixed (d) unified overall | **1.0 (held ≥0.967)** | **1.0 (held)** |
| R2–R12 routers (sample) | held | **22/22 · 35/35 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52** |
| R7/R12/LP verifiers | held | **44/44 · 44/44 · 32/32** |
| LP router | held | **43/43** |
| Router smoke | 12/12 | 12/12 |
| Pillars / hardneg smoke | 26/26 · 18/18 | held |
| `ent_never_on_python` | true | true |

Rise: 8→52 hits (**+550%** rate vs pre 0.1538→1.0; **+84.62 pp**) ≥80% freeze gate.

## Reinforce layer (gold-free, once)

1. **Router** — exclude Cloudflare `gates: fetch`; CloudFront `gates: PathPattern`; Vitess `gates: sharded`; CockroachDB `gates: GRANT`; Pinot `gates: ingestion`; CircleCI `gates: equal`; Drone `gates: event`; Maven `gates: activeByDefault`; sbt `gates: dependsOn`; Rails `gates: before_action`; Phoenix `gates: plug`; Flagger `gates: stepWeight`; Argo Rollouts `gates: setWeight`; Debezium `gates: op`; edge/CDN/DB/CI/build/framework/canary/CDC prose. R1–R12 patterns unchanged (R13–R16 not on tip base).
2. **Proposer** — none (all 44 heuristic-solvable).

## Freeze polish_r17

| Manifest | pct |
|----------|-----|
| `data/freeze_manifests/tip_moe_verifier_polish_r17_100pct_20260924_143628.json` | **100** |

Evidence: `data/freeze_metrics/codigo_vivo_tip_adv_r17_20260924.json`

## CLI

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r17
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r17_mixed_router.json
.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r17_python_items.json \
  --hardneg-router data/bench_live/hardneg_r17_mixed_router.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `data/bench_live/hardneg_r17_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r17.json`
- `data/frontier_moe_verifier_hardneg_r17.json`
- `data/frontier_moe_verifier_mixed_{cpu,unified}.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r17_20260924.json`
- `data/freeze_manifests/tip_moe_verifier_polish_r17_100pct_20260924_143628.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R17.md` (this file)

## Not folded

Leave tip-cv / tip-tti / tip-distance-* / tip-hardneg-r12..r16 / tip-inverse-r3 / tip-circ-expand / tip-future-track* / tip-choose-safest-n alone (fold queue far→R13→future-r3→circ→R14→R15→choose-n→R16). Side branch only.
