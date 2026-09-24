# Frontier — Código-vivo tip hardneg R15

**Branch:** `frontier/tip-hardneg-r15` → **FOLDED** into `frontier/codigo-vivo-tip`  
**Base tip:** `e0f3183` (`origin/frontier/codigo-vivo-tip` post tip-tti fold freeze pin)  
**When:** 2026-09-24 ~14:24 ET · Mac-111 (`074c6626-…`)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r15`  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`. No CloudAgent.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.
- R1 / R2 / R3 / R4 / R5 / R6 / R7 / R8 / R9 / R10 / R11 / label-protect fixtures must still hold after R15 reinforce.
- Do **not** touch tip-cv, tip-tti, tip-distance-mid, tip-distance-far, tip-hardneg-r12, tip-hardneg-r13, tip-hardneg-r14, tip-inverse-r3, tip-circ-expand, tip-future-track, tip-future-track-r2 (other lanes / fold queue). R15 stays side-only.

## R15 families (≠ R1–R14 / ≠ label-protect)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r15_mixed_router.json` | **52** | squid_proxy_gates, openresty_lua_gates, contour_route_gates, emissary_mapping_gates, zuul_filter_gates, django_mw_gates, laravel_mw_gates, gin_mw_gates, dynamodb_cond_gates, firestore_rules_gates, keycloak_realm_gates, falco_rule_gates, otel_sampler_gates, ray_actor_gates + ent/vision/base controls |
| `data/bench_live/hardneg_r15_python_items.json` | **44** | same coding themes; GT stdout harness-only |

HARD traps (pre-reinforce drops): Squid `gates: http_access`; OpenResty `gates: content_by_lua`; Contour `gates: retryPolicy`; Emissary `gates: hostname`; Zuul `gates: StripPrefix`; Django `gates: AuthenticationMiddleware`; Laravel `gates: VerifyCsrfToken`; Gin `gates: AuthRequired`; DynamoDB `gates: ConditionExpression`; Firestore `gates: allow read`; Keycloak `gates: realm-role`; Falco `gates: evt.type`; OTel `gates: parentbased`; Ray `gates: num_cpus`; base chat with those distractors + ENT_NEG.

Avoided (R9–R14): OpenAPI/Helm/…, AsyncAPI/Istio/…, Smithy/Linkerd/Cilium/…, Traefik/Envoy/NATS/Flux/Kong/Spinnaker/…, Nginx/HAProxy/Caddy/Redis/Postgres/Skaffold/Buildkite/Packer/Salt/Bazel/Dagger/Dagster/Hasura/NestJS, Apache httpd/Varnish/APISIX/Tyk/KrakenD/MongoDB/Cassandra/Jenkins/Vagrant/Chef/Pants/Prefect/FastAPI/Spring Security.

## Scores

| Surface | Pre-reinforce | Post-reinforce (1 layer) |
|---------|---------------|---------------------------|
| R15 router | 6/52 (**0.1154**) | **52/52 (1.0)** |
| R15 verifier alone loop | **1.0** (44/44) | **1.0** (44/44) |
| R15 unified loop | router-limited pre | **1.0** (44/44) |
| Mixed (d) unified overall | **1.0 (held ≥0.967)** | **1.0 (held)** |
| R1–R11 routers | held | **18/18 · 22/22 · 35/35 · 40/40 · 44/44 · 48/48 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52** |
| R7–R11 verifiers | held | **44/44 · 44/44 · 44/44 · 44/44 · 44/44** |
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

1. **Router** — exclude Squid `gates: http_access`; OpenResty `gates: content_by_lua`; Contour `gates: retryPolicy`; Emissary `gates: hostname`; Zuul `gates: StripPrefix`; Django `gates: AuthenticationMiddleware`; Laravel `gates: VerifyCsrfToken`; Gin `gates: AuthRequired`; DynamoDB `gates: ConditionExpression`; Firestore `gates: allow read`; Keycloak `gates: realm-role`; Falco `gates: evt.type`; OTel `gates: parentbased`; Ray `gates: num_cpus`; proxy/ingress/gateway/framework/DB/security/observability/orchestration prose. R1–R11 patterns unchanged (R12/R13/R14 not on tip base).
2. **Proposer** — none (all 44 heuristic-solvable).

## Freeze polish_r15

| Manifest | pct |
|----------|-----|
| `data/freeze_manifests/tip_moe_verifier_polish_r15_100pct_20260924_142410.json` | **100** |

Evidence: `data/freeze_metrics/codigo_vivo_tip_adv_r15_20260924.json`

## CLI

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r15
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r15_mixed_router.json
.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r15_python_items.json \
  --hardneg-router data/bench_live/hardneg_r15_mixed_router.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `data/bench_live/hardneg_r15_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r15.json`
- `data/frontier_moe_verifier_hardneg_r15.json`
- `data/frontier_moe_verifier_mixed_{cpu,unified}.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r15_20260924.json`
- `data/freeze_manifests/tip_moe_verifier_polish_r15_100pct_20260924_142410.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R15.md` (this file)

## Not folded (pre-fold note)

Leave tip-cv / tip-tti / tip-distance-mid / tip-distance-far / tip-hardneg-r12 / tip-hardneg-r13 / tip-hardneg-r14 / tip-inverse-r3 / tip-circ-expand / tip-future-track alone (fold queue mid→R12→inv-r3→far→R13→future→circ→R14). Side branch only.

## Folded into tip (2026-09-24 15:12:43 ET)

Cherry-pick `7ef18ce` onto tip `bc6902f` (post R14) → `a65dac6` / fold `4787c78` (merge R12+R13+R14+R15 gates_ops; keep tip STATUS+mixed/LP/r7–r11 JSON ours). Re-smoke on tip-cv: R15 **15/52 → 52/52 · 44/44** (side trail 6→52); R14 **52/52 · 44/44** held; mixed **1.0**; LP **64/64 · 42/42**; pillars **37/37**; circ **5/5**; R13/R12/R5/R7 held; tip vis BASE; RO adapters. Freeze `codigo_vivo_tip_r15_100pct_20260924_151243`.

**Not folded next:** choose-n / R16 / tti-cold / R17…R24.

## Fold re-smoke (2026-09-24 15:12:43 ET)

| Surface | Score |
|---------|-------|
| R15 router (tip before→after) | **15/52 → 52/52** |
| R15 verifier | **44/44** |
| R14 router · verifier | **52/52 · 44/44** |
| LP router · verifier | **64/64 · 42/42** |
| mixed (d) unified | **1.0** |
| pillars / hardneg smoke | **37/37 · 18/18** |
| circ axis (vis_circ_01…05) | **5/5** |
| R13 / R12 / R5 / R7 | **52/52 · 52/52 · 44/44 · 52/52** |
| `ent_never_on_python` | true |
| tip vis | BASE |
| Freeze | `codigo_vivo_tip_r15_100pct_20260924_151243` |
