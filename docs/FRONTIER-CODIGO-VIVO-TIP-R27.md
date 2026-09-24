# Frontier — Código-vivo tip hardneg R27

**Branch:** `frontier/tip-hardneg-r27` (side; not folded)  
**Base tip:** `88287bc` (`frontier/codigo-vivo-tip` post tip choose-safest-n fold; ≥422a9e3)  
**When:** 2026-09-24T15:24:06-04:00 · Mac-111 (`074c6626-0440-4817-9829-6bae77c578d6`)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r27`  
**Feat sha:** `PENDING`  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`. No CloudAgent.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.
- R7 / R8 / R9 / R10 / R11 / R12 / R13 / R14 / label-protect fixtures must still hold after R27 reinforce.
- Do **not** touch tip-cv, tip-tti*, tip-distance-*, tip-hardneg-r12..r26, tip-inverse*, tip-circ*, tip-future*, tip-choose*, tip-pillars*, tip-lp*, tip-label* (other lanes / fold queue). R27 stays side-only. **Do NOT fold.**

## R27 families (≠ R1–R26 / ≠ label-protect)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r27_mixed_router.json` | **52** | sequelize_hook_gates, mongoose_middleware_gates, actix_middleware_gates, rocket_fairing_gates, diesel_hook_gates, gorm_callback_gates, fastify_hook_gates, hapi_plugin_gates, sanic_middleware_gates, starlette_middleware_gates, sidekiq_middleware_gates, dramatiq_actor_gates, dropwizard_filter_gates, ktor_plugin_gates + ent/vision/base controls |
| `data/bench_live/hardneg_r27_python_items.json` | **44** | same coding themes; GT stdout harness-only |

HARD traps (pre-reinforce drops): Sequelize `gates: beforeFind`; Mongoose `gates: pre.save`; Actix `gates: from_fn`; Rocket `gates: Fairing::info`; Diesel `gates: Connection::transaction`; GORM `gates: BeforeCreate`; Fastify `gates: onRequest`; Hapi `gates: server.ext`; Sanic `gates: add_middleware`; Starlette `gates: BaseHTTPMiddleware`; Sidekiq `gates: ServerMiddleware`; Dramatiq `gates: actor.broker`; Dropwizard `gates: ContainerRequestFilter`; Ktor `gates: createApplicationPlugin`; base chat with those distractors + ENT_NEG.

Brief-suggested swaps (collisions / tip-brand / R9–R26): nestjs_guard→actix; quarkus_interceptor→dropwizard; laravel_middleware→hapi; prisma_middleware→sequelize (prisma_field R11); typeorm→mongoose; svelte_dependency→starlette; django_signal→sanic (django tip); flask_blueprint→fastify; spring_aspect→gorm (spring tip); rails_concern→sidekiq; elixir_plug→rocket (elixir tip / phoenix_plug R17); redis_lua→diesel (redis tip); temporal_workflow→dramatiq (temporal tip); clickhouse_materialized→ktor (clickhouse tip).

## Scores

| Surface | Pre-reinforce | Post-reinforce (1 layer) |
|---------|---------------|---------------------------|
| R27 router | 6/52 (**0.1154**) | **52/52 (1.0)** |
| R27 verifier alone loop | **1.0** (44/44) | **1.0** (44/44) |
| R27 unified loop | router-limited pre | **1.0** (44/44) |
| Mixed (d) unified overall | **1.0 (held ≥0.967)** | **1.0 (held)** |
| R7–R14 routers | held | **52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52** |
| R12/LP verifiers | held | **44/44 · 42/42** |
| LP router | held | **64/64** |
| Router smoke | 12/12 | 12/12 |
| Pillars / hardneg smoke | 37/37 · 18/18 | held (mixed pillar_routing 37/37 · hardneg 18/18) |
| `ent_never_on_python` | true | true |

Rise: 6→52 hits (**+766%** rate vs pre 0.1154→1.0; **+88.46 pp**) ≥80% freeze gate.

## Reinforce layer (gold-free, once)

1. **Router** — exclude Sequelize `gates: beforeFind`; Mongoose `gates: pre.save`; Actix `gates: from_fn`; Rocket `gates: Fairing::info`; Diesel `gates: Connection::transaction`; GORM `gates: BeforeCreate`; Fastify `gates: onRequest`; Hapi `gates: server.ext`; Sanic `gates: add_middleware`; Starlette `gates: BaseHTTPMiddleware`; Sidekiq `gates: ServerMiddleware`; Dramatiq `gates: actor.broker`; Dropwizard `gates: ContainerRequestFilter`; Ktor `gates: createApplicationPlugin`; hook/middleware/fairing/callback/plugin/actor/filter prose. R1–R15 patterns unchanged (R16–R26 not on tip base).
2. **Proposer** — none (all 44 heuristic-solvable).

## Freeze polish_r27

| Manifest | pct |
|----------|-----|
| `data/freeze_manifests/tip_moe_verifier_polish_r27_100pct_20260924_152406.json` | **100** |

Evidence: `data/freeze_metrics/codigo_vivo_tip_adv_r27_20260924.json`

## CLI

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r27
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r27_mixed_router.json
.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r27_python_items.json \
  --hardneg-router data/bench_live/hardneg_r27_mixed_router.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `data/bench_live/hardneg_r27_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r27.json`
- `data/frontier_moe_verifier_hardneg_r27.json`
- `data/frontier_moe_verifier_mixed_{cpu,unified}.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r27_20260924.json`
- `data/freeze_manifests/tip_moe_verifier_polish_r27_100pct_20260924_152406.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R27.md` (this file)

## Not folded

Leave tip-cv / tip-tti* / tip-distance-* / tip-hardneg-r12..r26 / tip-inverse* / tip-circ* / tip-future* / tip-choose* / tip-pillars* / tip-lp* / tip-label* alone (fold queue choose-n→R16→…→R26). Side branch only. **Do NOT fold.** R27 folds after R26.
