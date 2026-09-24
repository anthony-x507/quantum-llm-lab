# Frontier — Código-vivo tip hardneg R20

**Branch:** `frontier/tip-hardneg-r20` → **FOLDED** into `frontier/codigo-vivo-tip` (side; not folded)  
**Base tip:** `8beae21` (`frontier/codigo-vivo-tip` post tip R13 fold freeze/doc sha pin)  
**When:** 2026-09-24T14:52:49-04:00 ET · Mac-111 (`074c6626-…`)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r20`  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`. No CloudAgent.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.
- R7 / R8 / R9 / R10 / R11 / R12 / R13 / label-protect fixtures must still hold after R20 reinforce.
- Do **not** touch tip-cv, tip-tti*, tip-distance-*, tip-hardneg-r12..r19, tip-inverse*, tip-circ*, tip-future*, tip-choose*, tip-pillars*, tip-lp* (other lanes / fold queue). R20 stays side-only. Historical lock said side-only; superseded by fold below.

## R20 families (≠ R1–R19 / ≠ label-protect)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r20_mixed_router.json` | **52** | celery_task_gates, airbyte_stream_gates, supabase_policy_gates, trino_session_gates, vector_vrl_gates, fluentbit_filter_gates, thanos_query_gates, strimzi_topic_gates, tilt_resource_gates, mise_task_gates, cue_field_gates, nim_pragma_gates, hono_middleware_gates, axum_layer_gates + ent/vision/base controls |
| `data/bench_live/hardneg_r20_python_items.json` | **44** | same coding themes; GT stdout harness-only |

HARD traps (pre-reinforce drops): Celery `gates: bind`; Airbyte `gates: syncMode`; Supabase `gates: auth.uid`; Trino `gates: catalog`; Vector.dev `gates: parse_json`; Fluent Bit `gates: Match`; Thanos `gates: dedup`; Strimzi `gates: partitions`; Tilt `gates: trigger_mode`; Mise `gates: depends`; CUE `gates: close`; Nim `gates: push`; Hono `gates: createMiddleware`; Axum `gates: from_fn`; base chat with those distractors + ENT_NEG.

Avoided (R9–R19 + tip-claimed): OpenAPI/Helm/Justfile/Pulumi/…, AsyncAPI/Istio/Earthfile/…, Smithy/Zig comptime/Temporal/…, Traefik/Envoy/…, Nginx/HAProxy/…, Mage/Spark/ActiveMQ/Helmfile/Semaphore/Please/Django middleware/Laravel middleware/Akka/DuckDB/Calico/Longhorn/Loki/OTel Collector, and R12–R18 families.

## Scores

| Surface | Pre-reinforce | Post-reinforce (1 layer) |
|---------|---------------|---------------------------|
| R20 router | 6/52 (**0.1154**) | **52/52 (1.0)** |
| R20 verifier alone loop | **1.0** (44/44) | **1.0** (44/44) |
| R20 unified loop | router-limited pre | **1.0** (44/44) |
| Mixed (d) unified overall | **1.0 (held ≥0.967)** | **1.0 (held)** |
| R7–R13 routers | held | **52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52** |
| R12/LP verifiers | held | **44/44 · 32/32** |
| LP router | held | **43/43** |
| Router smoke | 12/12 | 12/12 |
| Pillars / hardneg smoke | 26/26 · 18/18 | held |
| `ent_never_on_python` | true | true |

Rise: 6→52 hits (**+766.6%** rate vs pre 0.1154→1.0; **+88.46 pp**) ≥80% freeze gate.

## Reinforce layer (gold-free, once)

1. **Router** — exclude Celery `gates: bind`; Airbyte `gates: syncMode`; Supabase `gates: auth.uid`; Trino `gates: catalog`; Vector `gates: parse_json`; Fluent Bit `gates: Match`; Thanos `gates: dedup`; Strimzi `gates: partitions`; Tilt `gates: trigger_mode`; Mise `gates: depends`; CUE `gates: close`; Nim `gates: push`; Hono `gates: createMiddleware`; Axum `gates: from_fn`; queue/ELT/BaaS/SQL/observability/log/metrics/Kafka/build/task/config/toolchain/framework/Rust prose. R1–R13 patterns unchanged (R14–R19 not on tip base).
2. **Proposer** — none (all 44 heuristic-solvable).

## Freeze polish_r20

| Manifest | pct |
|----------|-----|
| `data/freeze_manifests/tip_moe_verifier_polish_r20_100pct_20260924_145249.json` | **100** |

Evidence: `data/freeze_metrics/codigo_vivo_tip_adv_r20_20260924.json`

## CLI

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r20
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r20_mixed_router.json
.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r20_python_items.json \
  --hardneg-router data/bench_live/hardneg_r20_mixed_router.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `data/bench_live/hardneg_r20_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r20.json`
- `data/frontier_moe_verifier_hardneg_r20.json`
- `data/frontier_moe_verifier_mixed_{cpu,unified}.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r20_20260924.json`
- `data/freeze_manifests/tip_moe_verifier_polish_r20_100pct_20260924_145249.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R20.md` (this file)

## Not folded

Leave tip-cv / tip-tti* / tip-distance-* / tip-hardneg-r12..r19 / tip-inverse* / tip-circ* / tip-future* / tip-choose* / tip-pillars* alone (fold queue future-r3→circ→pillars→R14→R15→choose-n→R16→tti-cold→R17→R18→R19). Side branch only. Historical lock said side-only; superseded by fold below.

## Side trail (pre-fold)

Side branch polish completed before tip fold. Historical lock said side-only; superseded by fold below.

## Fold into tip (2026-09-24)

Cherry-pick `d9528bf` onto tip `9f2afbc`. Conflicts: STATUS+mixed/LP/r7–r12 JSON ours; router/verifier merged R12+R13+R14+R15+R16+R17+R18+R19+R20 gates_ops.

Freeze: `codigo_vivo_tip_r20_100pct_20260924_155357`

### Fold re-smoke (2026-09-24 15:53:57 ET)

| Surface | Result |
|---------|--------|
| R20 router / verifier | **7→52/52** / **44/44** |
| Side trail | **6→52** · rise_pp **88.46** |
| R19 / R18 / mixed (d) | **52/52·44/44 · 52/52·44/44 · 1.0** |
| pillars / hardneg smoke / circ | **37/37 · 18/18 · 5/5** |
| choose_n80 / tti-cold | **100%** / **~95%** freeze retained |
| `ent_never_on_python` | true |
| adapters RO | true |

### Artifacts

- `data/bench_live/hardneg_r20_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r20.json`
- `data/frontier_moe_verifier_hardneg_r20.json`
- `data/frontier_moe_verifier_mixed_{cpu,smoke,unified}_r20_fold.json`
- `data/freeze_metrics/codigo_vivo_tip_r20_{before,fold,adapter_ro,20260924}.json`
- `data/freeze_manifests/codigo_vivo_tip_r20_100pct_20260924_155357.json` (+ LATEST)
- `data/freeze_manifests/tip_moe_verifier_polish_r20_100pct_20260924_145249.json` (side polish retained)
- `docs/FRONTIER-CODIGO-VIVO-TIP-R20.md` (this file)

Fold SHA: `9f3ca74` · Base tip: `9f2afbc` · Side: `8cad9b3` / `d9528bf`

R21+ not folded. Tip vis stays BASE. RO `data/lora_adapter/`.
