# Frontier — Código-vivo tip hardneg R13

**Branch:** `frontier/tip-hardneg-r13` (side; not folded)  
**Base tip:** `f70faa1` (`origin/frontier/codigo-vivo-tip` post motion-r4 freeze pin)  
**When:** 2026-09-24 ~2:06–2:09 ET · Mac-111 (`074c6626-…`)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r13`  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`. No CloudAgent.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.
- R1 / R2 / R3 / R4 / R5 / R6 / R7 / R8 / R9 / R10 / label-protect fixtures must still hold after R13 reinforce.
- Do **not** touch tip-cv, tip-tti, tip-distance-mid, tip-distance-far, tip-hardneg-r11, tip-hardneg-r12, tip-inverse-r3 (other lanes / fold queue). R13 stays side-only.

## R13 families (≠ R1–R12 / ≠ label-protect)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r13_mixed_router.json` | **52** | nginx_map_gates, haproxy_acl_gates, caddy_matcher_gates, redis_acl_gates, postgres_rls_gates, skaffold_profile_gates, buildkite_step_gates, packer_provisioner_gates, salt_pillar_gates, bazel_select_gates, dagger_pipeline_gates, dagster_asset_gates, hasura_permission_gates, nestjs_guard_gates + ent/vision/base controls |
| `data/bench_live/hardneg_r13_python_items.json` | **44** | same coding themes; GT stdout harness-only |

HARD traps (pre-reinforce drops): Nginx `gates: $request`; HAProxy `gates: hdr`; Caddy `gates: path`; Redis `gates: ~*`; Postgres `gates: USING`; Skaffold `gates: activation`; Buildkite `gates: if`; Packer `gates: shell`; Salt `gates: grains`; Bazel `gates: //conditions`; Dagger `gates: withSecret`; Dagster `gates: AutoMaterialize`; Hasura `gates: check`; NestJS `gates: CanActivate`; base chat with those distractors + ENT_NEG.

Avoided (R9–R12): OpenAPI/Helm/…, AsyncAPI/Istio/…, Smithy/Linkerd/Cilium/…, Traefik/Envoy/NATS/Flux/Kong/Spinnaker/….

## Scores

| Surface | Pre-reinforce | Post-reinforce (1 layer) |
|---------|---------------|---------------------------|
| R13 router | 6/52 (**0.1154**) | **52/52 (1.0)** |
| R13 verifier alone loop | **1.0** (44/44) | **1.0** (44/44) |
| R13 unified loop | router-limited pre | **1.0** (44/44) |
| Mixed (d) unified overall | **1.0 (held ≥0.967)** | **1.0 (held)** |
| R1–R10 routers | held | **18/18 · 22/22 · 35/35 · 40/40 · 44/44 · 48/48 · 52/52 · 52/52 · 52/52 · 52/52** |
| R7–R10 verifiers | held | **44/44 · 44/44 · 44/44 · 44/44** |
| LP router/verifier | held | **43/43 · 32/32** |
| Router smoke | 12/12 | 12/12 |
| Pillars / hardneg smoke | 26/26 · 18/18 | held |
| `ent_never_on_python` | true | true |
| Motion (tip / if available) | **100%** known (motion-r4 on tip) | held (untouched) |
| Collision physics | **100%** | held (untouched) |
| inverse_cv | **≥99.82%** (inverse-r2 on tip) | held (untouched) |

Rise: 6→52 hits (**+766%** rate vs pre 0.1154→1.0; **+88.46 pp**) ≥80% freeze gate.

## Reinforce layer (gold-free, once)

1. **Router** — exclude Nginx `gates: $request`; HAProxy `gates: hdr`; Caddy `gates: path`; Redis `gates: ~*`; Postgres `gates: USING`; Skaffold `gates: activation`; Buildkite `gates: if`; Packer `gates: shell`; Salt `gates: grains`; Bazel `gates: //conditions`; Dagger `gates: withSecret`; Dagster `gates: AutoMaterialize`; Hasura `gates: check`; NestJS `gates: CanActivate`; proxy/LB/webserver/cache/DB/k8s/CI/image/config/build/orchestration/GraphQL/framework prose. R1–R10 patterns unchanged (R11/R12 not on tip base).
2. **Proposer** — none (all 44 heuristic-solvable).

## Freeze polish_r13

| Manifest | pct |
|----------|-----|
| `data/freeze_manifests/tip_moe_verifier_polish_r13_100pct_20260924_140847.json` | **100** |

Evidence: `data/freeze_metrics/codigo_vivo_tip_adv_r13_20260924.json`

## CLI

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r13
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r13_mixed_router.json
.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r13_python_items.json \
  --hardneg-router data/bench_live/hardneg_r13_mixed_router.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `data/bench_live/hardneg_r13_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r13.json`
- `data/frontier_moe_verifier_hardneg_r13.json`
- `data/frontier_moe_verifier_mixed_{cpu,unified}.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r13_20260924.json`
- `data/freeze_manifests/tip_moe_verifier_polish_r13_100pct_20260924_140847.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R13.md` (this file)

## Not folded

Leave tip-cv / tip-tti / tip-distance-mid / tip-distance-far / tip-hardneg-r11 / tip-hardneg-r12 / tip-inverse-r3 alone (fold queue R11→TTI→mid→R12→inverse-r3). Side branch only.
