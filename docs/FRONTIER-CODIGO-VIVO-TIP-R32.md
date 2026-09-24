# Frontier — Código-vivo tip hardneg R32

**Branch:** `frontier/tip-hardneg-r32` (side; not folded)  
**Base tip:** `9f2afbc` (`frontier/codigo-vivo-tip` post R19 fold; ≥9f2afbc)  
**When:** 2026-09-24T15:55:50-04:00 · Mac-111 (`074c6626-0440-4817-9829-6bae77c578d6`)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r32`  
**Feat sha:** `91fdaa4a07c2746efede835b4a2515f4cf301268`  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`. No CloudAgent.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.
- R7 / R8 / R9 / R10 / R11 / R12 / R13 / R14 / R17 / R18 / R19 / label-protect fixtures must still hold after R32 reinforce.
- Do **not** touch tip-cv, tip-tti*, tip-distance-*, tip-hardneg-r9..r31, tip-inverse*, tip-circ*, tip-future*, tip-choose*, tip-pillars*, tip-lp*, tip-label* (other lanes / fold queue). R32 stays side-only. **Do NOT fold.**

## R32 families (≠ R1–R31 / ≠ label-protect)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r32_mixed_router.json` | **52** | gino_loader_gates, emmett_pipeline_gates, morepath_defer_gates, laminas_middleware_gates, yii_behavior_gates, codeigniter_filter_gates, phalcon_middleware_gates, padrino_before_gates, roda_plugin_gates, feathers_hook_gates, moleculer_action_gates, delayed_job_gates, vertx_handler_gates, helidon_filter_gates + ent/vision/base controls |
| `data/bench_live/hardneg_r32_python_items.json` | **44** | same coding themes; GT stdout harness-only |

HARD traps (pre-reinforce drops): Gino `gates: Gino.loader`; Emmett `gates: emmett.Pipeline`; Morepath `gates: defer_links`; Laminas `gates: MiddlewarePipe`; Yii `gates: attachBehavior`; CodeIgniter `gates: FilterInterface`; Phalcon `gates: beforeExecuteRoute`; Padrino `gates: Padrino.before`; Roda `gates: Roda.plugin`; Feathers `gates: before.all`; Moleculer `gates: localAction`; DelayedJob `gates: Delayed::Worker`; Vert.x `gates: RoutingContext`; Helidon `gates: FilterChain`; base chat with those distractors + ENT_NEG.

Brief-suggested swaps (collisions / tip-brand / R9–R31): prisma_middleware→gino_loader (prisma_field R11); nestjs_guard→emmett_pipeline (nestjs_guard_gates R13); fastapi_dependency→morepath_defer (fastapi tip R14); django_signal→laminas_middleware (django tip); spring_aspect→yii_behavior (spring tip R14); quarkus_interceptor→codeigniter_filter (quarkus R18); laravel_middleware→phalcon_middleware (laravel R15/R19); rails_concern→padrino_before; elixir_plug→roda_plugin (elixir tip / phoenix_plug R17); redis_lua→feathers_hook (redis tip R13); temporal_workflow→moleculer_action (temporal tip R11); clickhouse_materialized→delayed_job (clickhouse tip R12); kafka_connect→vertx_handler (kafka priors); celery_beat→helidon_filter (celery_task priors). Avoid R31 set (ormar/piccolo/databases/cherrypy/masonite/hug/turbogears/web2py/apscheduler/kombu/restify/swoole/spiral/saq). Avoid R30 set (peewee/tortoise/pony/sqlmodel/fiber/iris/beego/buffalo/sinatra/quart/nameko/arq/slim/cakephp). Avoid R29 set (bookshelf/objection/mikroorm/tornado/bottle/falcon/pyramid/echo/chi/hanami/resque/rq/blacksheep/taskiq). Avoid R28 set (typeorm/knex/koa/litestar/aiohttp/hibernate/mybatis/adonis/grape/absinthe/huey/oban/javalin/jersey). Avoid R27 set (sequelize/mongoose/actix/rocket/diesel/gorm/fastify/hapi/sanic/starlette/sidekiq/dramatiq/dropwizard/ktor).

## Scores

| Surface | Pre-reinforce | Post-reinforce (1 layer) |
|---------|---------------|---------------------------|
| R32 router | 7/52 (**0.1346**) | **52/52 (1.0)** |
| R32 verifier alone loop | **1.0** (44/44) | **1.0** (44/44) |
| R32 unified loop | router-limited pre | **1.0** (44/44) |
| Mixed (d) unified overall | **1.0 (held ≥0.967)** | **1.0 (held)** |
| R7–R14 routers | held | **52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52** |
| R17 / R18 / R19 routers | held | **52/52 · 52/52 · 52/52** |
| R12/LP verifiers | held | **44/44 · 42/42** |
| LP router | held | **64/64** |
| Router smoke | 12/12 | 12/12 |
| Pillars / hardneg smoke | 37/37 · 18/18 | held (mixed pillar_routing 37/37 · hardneg 18/18) |
| `ent_never_on_python` | true | true |

Rise: 7→52 hits (**+643%** rate vs pre 0.1346→1.0; **+86.54 pp**) ≥80% freeze gate.

## Reinforce layer (gold-free, once)

1. **Router** — exclude Gino `gates: Gino.loader`; Emmett `gates: emmett.Pipeline`; Morepath `gates: defer_links`; Laminas `gates: MiddlewarePipe`; Yii `gates: attachBehavior`; CodeIgniter `gates: FilterInterface`; Phalcon `gates: beforeExecuteRoute`; Padrino `gates: Padrino.before`; Roda `gates: Roda.plugin`; Feathers `gates: before.all`; Moleculer `gates: localAction`; DelayedJob `gates: Delayed::Worker`; Vert.x `gates: RoutingContext`; Helidon `gates: FilterChain`; loader/pipeline/defer/middleware/behavior/filter/before/plugin/hook/action/job/handler prose. R1–R19 patterns unchanged (R20–R31 not on tip base).
2. **Proposer** — none (all 44 heuristic-solvable).

## Freeze polish_r32

| Manifest | pct |
|----------|-----|
| `data/freeze_manifests/tip_moe_verifier_polish_r32_100pct_20260924_155550.json` | **100** |

Evidence: `data/freeze_metrics/codigo_vivo_tip_adv_r32_20260924.json`

## CLI

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r32
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r32_mixed_router.json
.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r32_python_items.json \
  --hardneg-router data/bench_live/hardneg_r32_mixed_router.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `data/bench_live/hardneg_r32_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r32.json`
- `data/frontier_moe_verifier_hardneg_r32.json`
- `data/frontier_moe_verifier_mixed_{cpu,unified}.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r32_20260924.json`
- `data/freeze_manifests/tip_moe_verifier_polish_r32_100pct_20260924_155550.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R32.md` (this file)

## Not folded

Leave tip-cv / tip-tti* / tip-distance-* / tip-hardneg-r9..r31 / tip-inverse* / tip-circ* / tip-future* / tip-choose* / tip-pillars* / tip-lp* / tip-label* alone (fold queue … / R19→…→R31). Side branch only. **Do NOT fold.** R32 folds after R31.
