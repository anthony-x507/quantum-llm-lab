# Frontier — Código-vivo tip hardneg R30

**Branch:** `frontier/tip-hardneg-r30` (side; not folded)  
**Base tip:** `2e5c484` (`frontier/codigo-vivo-tip` post R17 fold; ≥a54b74c)  
**When:** 2026-09-24T15:45:06-04:00 · Mac-111 (`074c6626-0440-4817-9829-6bae77c578d6`)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r30`  
**Feat sha:** `4f1953cb776fd7803a73c90a31fcc4290e5fa9b9`  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`. No CloudAgent.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.
- R7 / R8 / R9 / R10 / R11 / R12 / R13 / R14 / R17 / label-protect fixtures must still hold after R30 reinforce.
- Do **not** touch tip-cv, tip-tti*, tip-distance-*, tip-hardneg-r9..r29, tip-inverse*, tip-circ*, tip-future*, tip-choose*, tip-pillars*, tip-lp*, tip-label* (other lanes / fold queue). R30 stays side-only. **Do NOT fold.**

## R30 families (≠ R1–R29 / ≠ label-protect)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r30_mixed_router.json` | **52** | peewee_signal_gates, tortoise_signal_gates, pony_hook_gates, sqlmodel_event_gates, fiber_middleware_gates, iris_middleware_gates, beego_filter_gates, buffalo_middleware_gates, sinatra_before_gates, quart_before_gates, nameko_entrypoint_gates, arq_job_gates, slim_middleware_gates, cakephp_middleware_gates + ent/vision/base controls |
| `data/bench_live/hardneg_r30_python_items.json` | **44** | same coding themes; GT stdout harness-only |

HARD traps (pre-reinforce drops): Peewee `gates: DatabaseProxy`; Tortoise `gates: Tortoise.init`; Pony `gates: db_session`; SQLModel `gates: SQLModelConfig`; Fiber `gates: fiber.Ctx`; Iris `gates: iris.Context`; Beego `gates: InsertFilter`; Buffalo `gates: buffalo.Context`; Sinatra `gates: before!`; Quart `gates: before_serving`; Nameko `gates: entrypoint.rpc`; ARQ `gates: arq.cron`; Slim `gates: MiddlewareDispatcher`; CakePHP `gates: MiddlewareQueue`; base chat with those distractors + ENT_NEG.

Brief-suggested swaps (collisions / tip-brand / R9–R29): prisma_middleware→peewee_signal (prisma_field R11); nestjs_guard→tortoise_signal (nestjs_guard_gates R13); fastapi_dependency→pony_hook (fastapi tip R14); django_signal→sqlmodel_event (django tip); spring_aspect→fiber_middleware (spring tip R14); quarkus_interceptor→iris_middleware (quarkus R18); laravel_middleware→beego_filter (laravel R15/R19); rails_concern→buffalo_middleware; elixir_plug→sinatra_before (elixir tip / phoenix_plug R17); redis_lua→quart_before (redis tip R13); temporal_workflow→nameko_entrypoint (temporal tip R11); clickhouse_materialized→arq_job (clickhouse tip R12); kafka_connect→slim_middleware (kafka priors); celery_beat→cakephp_middleware (celery_task priors). Avoid R29 set (bookshelf/objection/mikroorm/tornado/bottle/falcon/pyramid/echo/chi/hanami/resque/rq/blacksheep/taskiq). Avoid R28 set (typeorm/knex/koa/litestar/aiohttp/hibernate/mybatis/adonis/grape/absinthe/huey/oban/javalin/jersey). Avoid R27 set (sequelize/mongoose/actix/rocket/diesel/gorm/fastify/hapi/sanic/starlette/sidekiq/dramatiq/dropwizard/ktor).

## Scores

| Surface | Pre-reinforce | Post-reinforce (1 layer) |
|---------|---------------|---------------------------|
| R30 router | 6/52 (**0.1154**) | **52/52 (1.0)** |
| R30 verifier alone loop | **1.0** (44/44) | **1.0** (44/44) |
| R30 unified loop | router-limited pre | **1.0** (44/44) |
| Mixed (d) unified overall | **1.0 (held ≥0.967)** | **1.0 (held)** |
| R7–R14 routers | held | **52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52** |
| R17 router | held | **52/52** |
| R12/LP verifiers | held | **44/44 · 42/42** |
| LP router | held | **64/64** |
| Router smoke | 12/12 | 12/12 |
| Pillars / hardneg smoke | 37/37 · 18/18 | held (mixed pillar_routing 37/37 · hardneg 18/18) |
| `ent_never_on_python` | true | true |

Rise: 6→52 hits (**+766%** rate vs pre 0.1154→1.0; **+88.46 pp**) ≥80% freeze gate.

## Reinforce layer (gold-free, once)

1. **Router** — exclude Peewee `gates: DatabaseProxy`; Tortoise `gates: Tortoise.init`; Pony `gates: db_session`; SQLModel `gates: SQLModelConfig`; Fiber `gates: fiber.Ctx`; Iris `gates: iris.Context`; Beego `gates: InsertFilter`; Buffalo `gates: buffalo.Context`; Sinatra `gates: before!`; Quart `gates: before_serving`; Nameko `gates: entrypoint.rpc`; ARQ `gates: arq.cron`; Slim `gates: MiddlewareDispatcher`; CakePHP `gates: MiddlewareQueue`; signal/hook/event/middleware/filter/before/entrypoint/job prose. R1–R17 patterns unchanged (R18–R29 not on tip base).
2. **Proposer** — none (all 44 heuristic-solvable).

## Freeze polish_r30

| Manifest | pct |
|----------|-----|
| `data/freeze_manifests/tip_moe_verifier_polish_r30_100pct_20260924_154506.json` | **100** |

Evidence: `data/freeze_metrics/codigo_vivo_tip_adv_r30_20260924.json`

## CLI

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r30
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r30_mixed_router.json
.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r30_python_items.json \
  --hardneg-router data/bench_live/hardneg_r30_mixed_router.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `data/bench_live/hardneg_r30_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r30.json`
- `data/frontier_moe_verifier_hardneg_r30.json`
- `data/frontier_moe_verifier_mixed_{cpu,unified}.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r30_20260924.json`
- `data/freeze_manifests/tip_moe_verifier_polish_r30_100pct_20260924_154506.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R30.md` (this file)

## Not folded

Leave tip-cv / tip-tti* / tip-distance-* / tip-hardneg-r9..r29 / tip-inverse* / tip-circ* / tip-future* / tip-choose* / tip-pillars* / tip-lp* / tip-label* alone (fold queue … / R17→…→R29). Side branch only. **Do NOT fold.** R30 folds after R29.
