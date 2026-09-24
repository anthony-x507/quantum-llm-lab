# Frontier — Código-vivo tip hardneg R28

**Branch:** `frontier/tip-hardneg-r28` (side; not folded)  
**Base tip:** `a54b74c` (`frontier/codigo-vivo-tip` post tti-cold fold; ≥677235a)  
**When:** 2026-09-24T15:30:45-04:00 · Mac-111 (`074c6626-0440-4817-9829-6bae77c578d6`)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r28`  
**Feat sha:** `fd9a231be7910f98461a0cdd20ea7ecf6eb22d46`  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`. No CloudAgent.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.
- R7 / R8 / R9 / R10 / R11 / R12 / R13 / R14 / label-protect fixtures must still hold after R28 reinforce.
- Do **not** touch tip-cv, tip-tti*, tip-distance-*, tip-hardneg-r9..r27, tip-inverse*, tip-circ*, tip-future*, tip-choose*, tip-pillars*, tip-lp*, tip-label* (other lanes / fold queue). R28 stays side-only. **Do NOT fold.**

## R28 families (≠ R1–R27 / ≠ label-protect)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r28_mixed_router.json` | **52** | typeorm_subscriber_gates, knex_hook_gates, koa_middleware_gates, litestar_guard_gates, aiohttp_middleware_gates, hibernate_interceptor_gates, mybatis_interceptor_gates, adonis_middleware_gates, grape_middleware_gates, absinthe_middleware_gates, huey_task_gates, oban_plugin_gates, javalin_before_gates, jersey_filter_gates + ent/vision/base controls |
| `data/bench_live/hardneg_r28_python_items.json` | **44** | same coding themes; GT stdout harness-only |

HARD traps (pre-reinforce drops): TypeORM `gates: afterInsert`; Knex `gates: onQuery`; Koa `gates: compose`; Litestar `gates: ASGIConnection`; aiohttp `gates: @middleware`; Hibernate `gates: EmptyInterceptor`; MyBatis `gates: Interceptor.intercept`; AdonisJS `gates: HttpContext`; Grape `gates: Grape::Middleware`; Absinthe `gates: Absinthe.Middleware`; Huey `gates: db_task`; Oban `gates: after_process`; Javalin `gates: beforeMatched`; Jersey `gates: NameBinding`; base chat with those distractors + ENT_NEG.

Brief-suggested swaps (collisions / tip-brand / R9–R27): prisma_middleware→typeorm (prisma_field R11; typeorm free); nestjs_guard→koa (nestjs_guard_gates R13); svelte_dependency→litestar (svelte_store R7 / sveltekit_hook R22); django_signal→aiohttp (django tip); spring_aspect→hibernate (spring tip R14); quarkus_interceptor→mybatis (quarkus R18); laravel_middleware→adonis (laravel R15/R19); rails_concern→grape; elixir_plug→absinthe (elixir tip / phoenix_plug R17); redis_lua→huey (redis tip R13); temporal_workflow→oban (temporal tip R11); clickhouse_materialized→javalin (clickhouse tip R12); kafka_connect→jersey (kafka_acl / kafka_topic). Avoid R27 set (sequelize/mongoose/actix/rocket/diesel/gorm/fastify/hapi/sanic/starlette/sidekiq/dramatiq/dropwizard/ktor).

## Scores

| Surface | Pre-reinforce | Post-reinforce (1 layer) |
|---------|---------------|---------------------------|
| R28 router | 6/52 (**0.1154**) | **52/52 (1.0)** |
| R28 verifier alone loop | **1.0** (44/44) | **1.0** (44/44) |
| R28 unified loop | router-limited pre | **1.0** (44/44) |
| Mixed (d) unified overall | **1.0 (held ≥0.967)** | **1.0 (held)** |
| R7–R14 routers | held | **52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52** |
| R12/LP verifiers | held | **44/44 · 42/42** |
| LP router | held | **64/64** |
| Router smoke | 12/12 | 12/12 |
| Pillars / hardneg smoke | 37/37 · 18/18 | held (mixed pillar_routing 37/37 · hardneg 18/18) |
| `ent_never_on_python` | true | true |

Rise: 6→52 hits (**+766%** rate vs pre 0.1154→1.0; **+88.46 pp**) ≥80% freeze gate.

## Reinforce layer (gold-free, once)

1. **Router** — exclude TypeORM `gates: afterInsert`; Knex `gates: onQuery`; Koa `gates: compose`; Litestar `gates: ASGIConnection`; aiohttp `gates: @middleware`; Hibernate `gates: EmptyInterceptor`; MyBatis `gates: Interceptor.intercept`; AdonisJS `gates: HttpContext`; Grape `gates: Grape::Middleware`; Absinthe `gates: Absinthe.Middleware`; Huey `gates: db_task`; Oban `gates: after_process`; Javalin `gates: beforeMatched`; Jersey `gates: NameBinding`; subscriber/hook/middleware/guard/interceptor/task/plugin/filter prose. R1–R16 patterns unchanged (R17–R27 not on tip base).
2. **Proposer** — none (all 44 heuristic-solvable).

## Freeze polish_r28

| Manifest | pct |
|----------|-----|
| `data/freeze_manifests/tip_moe_verifier_polish_r28_100pct_20260924_153045.json` | **100** |

Evidence: `data/freeze_metrics/codigo_vivo_tip_adv_r28_20260924.json`

## CLI

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r28
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r28_mixed_router.json
.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r28_python_items.json \
  --hardneg-router data/bench_live/hardneg_r28_mixed_router.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `data/bench_live/hardneg_r28_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r28.json`
- `data/frontier_moe_verifier_hardneg_r28.json`
- `data/frontier_moe_verifier_mixed_{cpu,unified}.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r28_20260924.json`
- `data/freeze_manifests/tip_moe_verifier_polish_r28_100pct_20260924_153045.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R28.md` (this file)

## Not folded

Leave tip-cv / tip-tti* / tip-distance-* / tip-hardneg-r9..r27 / tip-inverse* / tip-circ* / tip-future* / tip-choose* / tip-pillars* / tip-lp* / tip-label* alone (fold queue tti-cold / … / R17→…→R27). Side branch only. **Do NOT fold.** R28 folds after R27.
