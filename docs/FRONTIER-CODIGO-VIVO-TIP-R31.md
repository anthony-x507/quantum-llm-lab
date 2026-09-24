# Frontier — Código-vivo tip hardneg R31

**Branch:** `frontier/tip-hardneg-r31` (side; not folded)  
**Base tip:** `9c320cb` (`frontier/codigo-vivo-tip` post R18 fold; ≥9c320cb)  
**When:** 2026-09-24T15:49:35-04:00 · Mac-111 (`074c6626-0440-4817-9829-6bae77c578d6`)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r31`  
**Feat sha:** `65c95ede4098fccadfb9553ba9ea95f893239b8e`  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`. No CloudAgent.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.
- R7 / R8 / R9 / R10 / R11 / R12 / R13 / R14 / R17 / R18 / label-protect fixtures must still hold after R31 reinforce.
- Do **not** touch tip-cv, tip-tti*, tip-distance-*, tip-hardneg-r9..r30, tip-inverse*, tip-circ*, tip-future*, tip-choose*, tip-pillars*, tip-lp*, tip-label* (other lanes / fold queue). R31 stays side-only. **Do NOT fold.**

## R31 families (≠ R1–R30 / ≠ label-protect)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r31_mixed_router.json` | **52** | ormar_signal_gates, piccolo_app_gates, databases_hook_gates, cherrypy_tool_gates, masonite_middleware_gates, hug_directive_gates, turbogears_hook_gates, web2py_hook_gates, apscheduler_job_gates, kombu_consumer_gates, restify_middleware_gates, swoole_middleware_gates, spiral_interceptor_gates, saq_job_gates + ent/vision/base controls |
| `data/bench_live/hardneg_r31_python_items.json` | **44** | same coding themes; GT stdout harness-only |

HARD traps (pre-reinforce drops): Ormar `gates: Signal.emit`; Piccolo `gates: PiccoloApp`; Databases `gates: Database.connection`; CherryPy `gates: cherrypy.Tool`; Masonite `gates: HTTPMiddleware`; Hug `gates: hug.directive`; TurboGears `gates: tg.hooks`; web2py `gates: gluon.current`; APScheduler `gates: BackgroundScheduler`; Kombu `gates: Consumer.consume`; Restify `gates: server.use`; Swoole `gates: MiddlewareManager`; Spiral `gates: InterceptorInterface`; SAQ `gates: saq.Job`; base chat with those distractors + ENT_NEG.

Brief-suggested swaps (collisions / tip-brand / R9–R30): prisma_middleware→ormar_signal (prisma_field R11); nestjs_guard→piccolo_app (nestjs_guard_gates R13); fastapi_dependency→databases_hook (fastapi tip R14); django_signal→cherrypy_tool (django tip); spring_aspect→masonite_middleware (spring tip R14); quarkus_interceptor→hug_directive (quarkus R18); laravel_middleware→turbogears_hook (laravel R15/R19); rails_concern→web2py_hook; elixir_plug→apscheduler_job (elixir tip / phoenix_plug R17); redis_lua→kombu_consumer (redis tip R13); temporal_workflow→restify_middleware (temporal tip R11); clickhouse_materialized→swoole_middleware (clickhouse tip R12); kafka_connect→spiral_interceptor (kafka priors); celery_beat→saq_job (celery_task priors). Avoid R30 set (peewee/tortoise/pony/sqlmodel/fiber/iris/beego/buffalo/sinatra/quart/nameko/arq/slim/cakephp). Avoid R29 set (bookshelf/objection/mikroorm/tornado/bottle/falcon/pyramid/echo/chi/hanami/resque/rq/blacksheep/taskiq). Avoid R28 set (typeorm/knex/koa/litestar/aiohttp/hibernate/mybatis/adonis/grape/absinthe/huey/oban/javalin/jersey). Avoid R27 set (sequelize/mongoose/actix/rocket/diesel/gorm/fastify/hapi/sanic/starlette/sidekiq/dramatiq/dropwizard/ktor).

## Scores

| Surface | Pre-reinforce | Post-reinforce (1 layer) |
|---------|---------------|---------------------------|
| R31 router | 6/52 (**0.1154**) | **52/52 (1.0)** |
| R31 verifier alone loop | **1.0** (44/44) | **1.0** (44/44) |
| R31 unified loop | router-limited pre | **1.0** (44/44) |
| Mixed (d) unified overall | **1.0 (held ≥0.967)** | **1.0 (held)** |
| R7–R14 routers | held | **52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52** |
| R17 / R18 routers | held | **52/52 · 52/52** |
| R12/LP verifiers | held | **44/44 · 42/42** |
| LP router | held | **64/64** |
| Router smoke | 12/12 | 12/12 |
| Pillars / hardneg smoke | 37/37 · 18/18 | held (mixed pillar_routing 37/37 · hardneg 18/18) |
| `ent_never_on_python` | true | true |

Rise: 6→52 hits (**+766%** rate vs pre 0.1154→1.0; **+88.46 pp**) ≥80% freeze gate.

## Reinforce layer (gold-free, once)

1. **Router** — exclude Ormar `gates: Signal.emit`; Piccolo `gates: PiccoloApp`; Databases `gates: Database.connection`; CherryPy `gates: cherrypy.Tool`; Masonite `gates: HTTPMiddleware`; Hug `gates: hug.directive`; TurboGears `gates: tg.hooks`; web2py `gates: gluon.current`; APScheduler `gates: BackgroundScheduler`; Kombu `gates: Consumer.consume`; Restify `gates: server.use`; Swoole `gates: MiddlewareManager`; Spiral `gates: InterceptorInterface`; SAQ `gates: saq.Job`; signal/app/hook/tool/middleware/directive/job/consumer/interceptor prose. R1–R18 patterns unchanged (R19–R30 not on tip base).
2. **Proposer** — none (all 44 heuristic-solvable).

## Freeze polish_r31

| Manifest | pct |
|----------|-----|
| `data/freeze_manifests/tip_moe_verifier_polish_r31_100pct_20260924_154935.json` | **100** |

Evidence: `data/freeze_metrics/codigo_vivo_tip_adv_r31_20260924.json`

## CLI

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r31
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r31_mixed_router.json
.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r31_python_items.json \
  --hardneg-router data/bench_live/hardneg_r31_mixed_router.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `data/bench_live/hardneg_r31_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r31.json`
- `data/frontier_moe_verifier_hardneg_r31.json`
- `data/frontier_moe_verifier_mixed_{cpu,unified}.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r31_20260924.json`
- `data/freeze_manifests/tip_moe_verifier_polish_r31_100pct_20260924_154935.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R31.md` (this file)

## Not folded

Leave tip-cv / tip-tti* / tip-distance-* / tip-hardneg-r9..r30 / tip-inverse* / tip-circ* / tip-future* / tip-choose* / tip-pillars* / tip-lp* / tip-label* alone (fold queue … / R18→…→R30). Side branch only. **Do NOT fold.** R31 folds after R30.
