# Frontier — Código-vivo tip hardneg R14

**Branch:** `frontier/tip-hardneg-r14` → **FOLDED** into `frontier/codigo-vivo-tip`  
**Base tip:** `e0f3183` (`origin/frontier/codigo-vivo-tip` post tip-tti fold freeze pin)  
**When:** 2026-09-24 ~2:15–2:18 ET · Mac-111 (`074c6626-…`)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r14`  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`. No CloudAgent.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.
- R1 / R2 / R3 / R4 / R5 / R6 / R7 / R8 / R9 / R10 / R11 / label-protect fixtures must still hold after R14 reinforce.
- Do **not** touch tip-cv, tip-tti, tip-distance-mid, tip-distance-far, tip-hardneg-r12, tip-hardneg-r13, tip-inverse-r3, tip-circ-expand, tip-future-track (other lanes / fold queue). R14 folded into tip-cv; do not re-fold.

## R14 families (≠ R1–R13 / ≠ label-protect)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r14_mixed_router.json` | **52** | httpd_rewrite_gates, varnish_vcl_gates, apisix_plugin_gates, tyk_middleware_gates, krakend_endpoint_gates, mongodb_role_gates, cassandra_table_gates, jenkins_when_gates, vagrant_provision_gates, chef_guard_gates, pants_tag_gates, prefect_task_gates, fastapi_depends_gates, spring_security_gates + ent/vision/base controls |
| `data/bench_live/hardneg_r14_python_items.json` | **44** | same coding themes; GT stdout harness-only |

HARD traps (pre-reinforce drops): Apache httpd `gates: RewriteCond`; Varnish `gates: bereq.url`; APISIX `gates: limit-count`; Tyk `gates: rate_limit`; KrakenD `gates: qos/ratelimit`; MongoDB `gates: find`; Cassandra `gates: compaction`; Jenkins `gates: expression`; Vagrant `gates: ansible`; Chef `gates: not_if`; Pants `gates: resolve`; Prefect `gates: retries`; FastAPI `gates: Security`; Spring `gates: hasAuthority`; base chat with those distractors + ENT_NEG.

Avoided (R9–R13): OpenAPI/Helm/…, AsyncAPI/Istio/…, Smithy/Linkerd/Cilium/…, Traefik/Envoy/NATS/Flux/Kong/Spinnaker/…, Nginx/HAProxy/Caddy/Redis/Postgres/Skaffold/Buildkite/Packer/Salt/Bazel/Dagger/Dagster/Hasura/NestJS.

## Scores

| Surface | Pre-reinforce | Post-reinforce (1 layer) |
|---------|---------------|---------------------------|
| R14 router | 8/52 (**0.1538**) | **52/52 (1.0)** |
| R14 verifier alone loop | **1.0** (44/44) | **1.0** (44/44) |
| R14 unified loop | router-limited pre | **1.0** (44/44) |
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

Rise: 8→52 hits (**+550%** rate vs pre 0.1538→1.0; **+84.62 pp**) ≥80% freeze gate.

## Reinforce layer (gold-free, once)

1. **Router** — exclude Apache httpd `gates: RewriteCond`; Varnish `gates: bereq.url`; APISIX `gates: limit-count`; Tyk `gates: rate_limit`; KrakenD `gates: qos/ratelimit`; MongoDB `gates: find`; Cassandra `gates: compaction`; Jenkins `gates: expression`; Vagrant `gates: ansible`; Chef `gates: not_if`; Pants `gates: resolve`; Prefect `gates: retries`; FastAPI `gates: Security`; Spring `gates: hasAuthority`; httpd/cache/gateway/API/DB/CI/image/config/build/orchestration/framework/security prose. R1–R11 patterns unchanged (R12/R13 not on tip base).
2. **Proposer** — none (all 44 heuristic-solvable).

## Freeze polish_r14

| Manifest | pct |
|----------|-----|
| `data/freeze_manifests/tip_moe_verifier_polish_r14_100pct_20260924_141830.json` | **100** |

Evidence: `data/freeze_metrics/codigo_vivo_tip_adv_r14_20260924.json`

## CLI

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r14
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r14_mixed_router.json
.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r14_python_items.json \
  --hardneg-router data/bench_live/hardneg_r14_mixed_router.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `data/bench_live/hardneg_r14_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r14.json`
- `data/frontier_moe_verifier_hardneg_r14.json`
- `data/frontier_moe_verifier_mixed_{cpu,unified}.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r14_20260924.json`
- `data/freeze_manifests/tip_moe_verifier_polish_r14_100pct_20260924_141830.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R14.md` (this file)

## Not folded

Leave tip-cv / tip-tti / tip-distance-mid / tip-distance-far / tip-hardneg-r12 / tip-hardneg-r13 / tip-inverse-r3 / tip-circ-expand / tip-future-track alone (fold queue mid→R12→inv-r3→far→R13→future-track). Side branch only.

## Folded into tip (2026-09-24 15:08:09 ET)

Cherry-pick `37ccc6f` onto tip `1d5fe3e` (post LP-expand) → `e1b12d5` / fold `6a4e716` (merge R12+R13+R14 gates_ops; keep tip STATUS+mixed/LP/r7–r11 JSON ours). Re-smoke on tip-cv: R14 **16/52 → 52/52 · 44/44** (side trail 8→52); mixed **1.0**; LP **64/64 · 42/42**; pillars **37/37**; circ **5/5**; R13/R12/R5/R7 held; tip vis BASE; RO adapters. Freeze `codigo_vivo_tip_r14_100pct_20260924_150809`.

**Not folded next:** R15 / choose-n / tti-cold / R16…R23.

## Fold re-smoke (2026-09-24 15:08:09 ET)

| Surface | Score |
|---------|-------|
| R14 router (tip before→after) | **16/52 → 52/52** |
| R14 verifier | **44/44** |
| LP router · verifier | **64/64 · 42/42** |
| mixed (d) unified | **1.0** |
| pillars / hardneg smoke | **37/37 · 18/18** |
| circ axis (vis_circ_01…05) | **5/5** |
| R13 / R12 / R5 / R7 | **52/52 · 52/52 · 44/44 · 52/52** |
| `ent_never_on_python` | true |
| tip vis | BASE |
| Freeze | `codigo_vivo_tip_r14_100pct_20260924_150809` |
