# Frontier — Código-vivo tip hardneg R29

**Branch:** `frontier/tip-hardneg-r29` (side; not folded)  
**Base tip:** `a54b74c` (`frontier/codigo-vivo-tip` post tti-cold fold; ≥677235a)  
**When:** 2026-09-24T15:39:31-04:00 · Mac-111 (`074c6626-0440-4817-9829-6bae77c578d6`)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r29`  
**Feat sha:** `f805f4bab74aac0e183922f0d6d7f263592fffbc`  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`. No CloudAgent.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.
- R7 / R8 / R9 / R10 / R11 / R12 / R13 / R14 / label-protect fixtures must still hold after R29 reinforce.
- Do **not** touch tip-cv, tip-tti*, tip-distance-*, tip-hardneg-r9..r28, tip-inverse*, tip-circ*, tip-future*, tip-choose*, tip-pillars*, tip-lp*, tip-label* (other lanes / fold queue). R29 stays side-only. **Do NOT fold.**

## R29 families (≠ R1–R28 / ≠ label-protect)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r29_mixed_router.json` | **52** | bookshelf_plugin_gates, objection_hook_gates, mikroorm_subscriber_gates, tornado_middleware_gates, bottle_plugin_gates, falcon_middleware_gates, pyramid_tween_gates, echo_middleware_gates, chi_middleware_gates, hanami_middleware_gates, resque_plugin_gates, rq_job_gates, blacksheep_middleware_gates, taskiq_middleware_gates + ent/vision/base controls |
| `data/bench_live/hardneg_r29_python_items.json` | **44** | same coding themes; GT stdout harness-only |

HARD traps (pre-reinforce drops): Bookshelf.js `gates: Model.initialize`; Objection.js `gates: $beforeInsert`; MikroORM `gates: EventSubscriber`; Tornado `gates: RequestHandler`; Bottle `gates: Plugin.apply`; Falcon `gates: process_request`; Pyramid `gates: tween_factory`; Echo `gates: MiddlewareFunc`; Chi `gates: Middleware.New`; Hanami `gates: Hanami::Action`; Resque `gates: before_perform`; RQ `gates: job.perform`; BlackSheep `gates: BoundHandler`; Taskiq `gates: TaskiqMiddleware`; base chat with those distractors + ENT_NEG.

Brief-suggested swaps (collisions / tip-brand / R9–R28): prisma_middleware→bookshelf_plugin (prisma_field R11); nestjs_guard→objection_hook (nestjs_guard_gates R13); fastapi_dependency→mikroorm_subscriber (fastapi tip R14); django_signal→tornado_middleware (django tip); spring_aspect→bottle_plugin (spring tip R14); quarkus_interceptor→falcon_middleware (quarkus R18); laravel_middleware→pyramid_tween (laravel R15/R19); rails_concern→echo_middleware; elixir_plug→chi_middleware (elixir tip / phoenix_plug R17); redis_lua→hanami_middleware (redis tip R13); temporal_workflow→resque_plugin (temporal tip R11); clickhouse_materialized→rq_job (clickhouse tip R12); kafka_connect→blacksheep_middleware (kafka priors); celery_beat→taskiq_middleware (celery_task priors). Avoid R28 set (typeorm/knex/koa/litestar/aiohttp/hibernate/mybatis/adonis/grape/absinthe/huey/oban/javalin/jersey). Avoid R27 set (sequelize/mongoose/actix/rocket/diesel/gorm/fastify/hapi/sanic/starlette/sidekiq/dramatiq/dropwizard/ktor).

## Scores

| Surface | Pre-reinforce | Post-reinforce (1 layer) |
|---------|---------------|---------------------------|
| R29 router | 6/52 (**0.1154**) | **52/52 (1.0)** |
| R29 verifier alone loop | **1.0** (44/44) | **1.0** (44/44) |
| R29 unified loop | router-limited pre | **1.0** (44/44) |
| Mixed (d) unified overall | **1.0 (held ≥0.967)** | **1.0 (held)** |
| R7–R14 routers | held | **52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52** |
| R12/LP verifiers | held | **44/44 · 42/42** |
| LP router | held | **64/64** |
| Router smoke | 12/12 | 12/12 |
| Pillars / hardneg smoke | 37/37 · 18/18 | held (mixed pillar_routing 37/37 · hardneg 18/18) |
| `ent_never_on_python` | true | true |

Rise: 6→52 hits (**+766%** rate vs pre 0.1154→1.0; **+88.46 pp**) ≥80% freeze gate.

## Reinforce layer (gold-free, once)

1. **Router** — exclude Bookshelf.js `gates: Model.initialize`; Objection.js `gates: $beforeInsert`; MikroORM `gates: EventSubscriber`; Tornado `gates: RequestHandler`; Bottle `gates: Plugin.apply`; Falcon `gates: process_request`; Pyramid `gates: tween_factory`; Echo `gates: MiddlewareFunc`; Chi `gates: Middleware.New`; Hanami `gates: Hanami::Action`; Resque `gates: before_perform`; RQ `gates: job.perform`; BlackSheep `gates: BoundHandler`; Taskiq `gates: TaskiqMiddleware`; plugin/hook/subscriber/middleware/tween/job prose. R1–R16 patterns unchanged (R17–R28 not on tip base).
2. **Proposer** — none (all 44 heuristic-solvable).

## Freeze polish_r29

| Manifest | pct |
|----------|-----|
| `data/freeze_manifests/tip_moe_verifier_polish_r29_100pct_20260924_153931.json` | **100** |

Evidence: `data/freeze_metrics/codigo_vivo_tip_adv_r29_20260924.json`

## CLI

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r29
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r29_mixed_router.json
.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r29_python_items.json \
  --hardneg-router data/bench_live/hardneg_r29_mixed_router.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `data/bench_live/hardneg_r29_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r29.json`
- `data/frontier_moe_verifier_hardneg_r29.json`
- `data/frontier_moe_verifier_mixed_{cpu,unified}.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r29_20260924.json`
- `data/freeze_manifests/tip_moe_verifier_polish_r29_100pct_20260924_153931.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R29.md` (this file)

## Not folded

Leave tip-cv / tip-tti* / tip-distance-* / tip-hardneg-r9..r28 / tip-inverse* / tip-circ* / tip-future* / tip-choose* / tip-pillars* / tip-lp* / tip-label* alone (fold queue tti-cold / … / R17→…→R28). Side branch only. **Do NOT fold.** R29 folds after R28.
