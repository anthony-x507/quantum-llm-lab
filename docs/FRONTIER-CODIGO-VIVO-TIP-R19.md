# Frontier — Código-vivo tip hardneg R19

**Branch:** `frontier/tip-hardneg-r19` → **FOLDED** into `frontier/codigo-vivo-tip`  
**Base tip:** `845a292` (`frontier/codigo-vivo-tip` post tip hardneg R13 polish; ≥ brief pin `f052420`)  
**When:** 2026-09-24 ~2026-09-24T14:46:42-04:00 ET · Mac-111 (`074c6626-…`)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r19`  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`. No CloudAgent.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.
- R7 / R8 / R9 / R10 / R11 / R12 / R13 / label-protect fixtures must still hold after R19 reinforce.
- Do **not** touch tip-cv, tip-tti*, tip-distance-*, tip-hardneg-r12..r18, tip-inverse-r3, tip-circ-expand, tip-future-track*, tip-choose-safest-n, tip-pillars* (other lanes / fold queue). R19 stays side-only. **Do NOT fold.**

## R19 families (≠ R1–R18 / ≠ label-protect)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r19_mixed_router.json` | **52** | mage_block_gates, spark_conf_gates, activemq_destination_gates, helmfile_release_gates, semaphore_block_gates, please_build_gates, django_middleware_gates, laravel_middleware_gates, akka_receive_gates, duckdb_pragma_gates, calico_network_gates, longhorn_replica_gates, loki_pipeline_gates, otelcol_processor_gates + ent/vision/base controls |
| `data/bench_live/hardneg_r19_python_items.json` | **44** | same coding themes; GT stdout harness-only |

HARD traps (pre-reinforce drops): Mage AI `gates: data_exporter`; Apache Spark `gates: spark.sql.adaptive`; ActiveMQ `gates: queuePriority`; Helmfile `gates: installed`; Semaphore CI `gates: prologue`; Please Build `gates: plz`; Django `gates: MIDDLEWARE`; Laravel `gates: terminate`; Akka `gates: Receive`; DuckDB `gates: threads`; Calico `gates: selectorExpr`; Longhorn `gates: SoftAntiAffinity`; Grafana Loki `gates: pipeline_stages`; OpenTelemetry Collector `gates: memory_limiter`; base chat with those distractors + ENT_NEG.

Avoided (R9–R18 + tip-claimed): OpenAPI/Helm/…, AsyncAPI/Istio/Nomad/Vault/ArgoCD/Tekton/…, Smithy/Prisma/Ansible/Consul/Linkerd/Cilium/Airflow/Kafka/Prometheus/Kyverno/Gradle/…, Traefik/Envoy/NATS/Flux/Kong/Spinnaker/…, Nginx/HAProxy/Caddy/…, Apache httpd/Varnish/APISIX/…, Squid/OpenResty/Contour/…, ATS/CoreDNS/Pulsar/Redpanda/…, Cloudflare/CloudFront/Vitess/Cockroach/Pinot/CircleCI/Drone/Maven/sbt/Rails/Phoenix/Flagger/Argo Rollouts/Debezium, AWS ALB/Azure Front Door/GCP URL Map/Hudi/Iceberg/Flink/NiFi/Concourse/Woodpecker/TeamCity/Cargo/Go build tags/Quarkus/Micronaut.

## Scores

| Surface | Pre-reinforce | Post-reinforce (1 layer) |
|---------|---------------|---------------------------|
| R19 router | 6/52 (**0.1154**) | **52/52 (1.0)** |
| R19 verifier alone loop | **1.0** (44/44) | **1.0** (44/44) |
| R19 unified loop | router-limited pre | **1.0** (44/44) |
| Mixed (d) unified overall | **1.0 (held ≥0.967)** | **1.0 (held)** |
| R7–R13 routers | held | **52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52** |
| R12/LP verifiers | held | **44/44 · 32/32** |
| LP router | held | **43/43** |
| Router smoke | 12/12 | 12/12 |
| Pillars / hardneg smoke | 26/26 · 18/18 | held |
| `ent_never_on_python` | true | true |

Rise: 6→52 hits (**+766%** rate vs pre 0.1154→1.0; **+88.46 pp**) ≥80% freeze gate.

## Reinforce layer (gold-free, once)

1. **Router** — exclude Mage `gates: data_exporter`; Spark `gates: spark.sql.adaptive`; ActiveMQ `gates: queuePriority`; Helmfile `gates: installed`; Semaphore `gates: prologue`; Please `gates: plz`; Django `gates: MIDDLEWARE`; Laravel `gates: terminate`; Akka `gates: Receive`; DuckDB `gates: threads`; Calico `gates: selectorExpr`; Longhorn `gates: SoftAntiAffinity`; Loki `gates: pipeline_stages`; OTel Collector `gates: memory_limiter`; mesh/compute/messaging/GitOps/actor/DB/network/storage/observability prose. R1–R13 patterns unchanged (R14–R18 not on tip base).
2. **Proposer** — none (all 44 heuristic-solvable).

## Freeze polish_r19

| Manifest | pct |
|----------|-----|
| `data/freeze_manifests/tip_moe_verifier_polish_r19_100pct_20260924_144642.json` | **100** |

Evidence: `data/freeze_metrics/codigo_vivo_tip_adv_r19_20260924.json`

## CLI

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r19
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r19_mixed_router.json
.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r19_python_items.json \
  --hardneg-router data/bench_live/hardneg_r19_mixed_router.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `data/bench_live/hardneg_r19_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r19.json`
- `data/frontier_moe_verifier_hardneg_r19.json`
- `data/frontier_moe_verifier_mixed_{cpu,unified}.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r19_20260924.json`
- `data/freeze_manifests/tip_moe_verifier_polish_r19_100pct_20260924_144642.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R19.md` (this file)

## Side trail (pre-fold)

Side branch polish completed before tip fold. Historical lock said side-only; superseded by fold below.

## Fold into tip (2026-09-24)

Cherry-pick `f20e327` onto tip `9c320cb`. Conflicts: STATUS+mixed/LP/r7–r12 JSON ours; router/verifier merged R12+R13+R14+R15+R16+R17+R18+R19 gates_ops.

Freeze: `codigo_vivo_tip_r19_100pct_20260924_154857`

### Fold re-smoke (2026-09-24 15:48:57 ET)

| Surface | Result |
|---------|--------|
| R19 router / verifier | **18→52/52** / **44/44** |
| Side trail | **6→52** · rise_pp **88.46** |
| R18 / R17 / mixed (d) | **52/52·44/44 · 52/52·44/44 · 1.0** |
| pillars / hardneg smoke / circ | **37/37 · 18/18 · 5/5** |
| choose_n80 / tti-cold | **100%** / **~95%** freeze retained |
| `ent_never_on_python` | true |
| adapters RO | true |

### Artifacts

- `data/bench_live/hardneg_r19_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r19.json`
- `data/frontier_moe_verifier_hardneg_r19.json`
- `data/frontier_moe_verifier_mixed_{cpu,smoke,unified}_r19_fold.json`
- `data/freeze_metrics/codigo_vivo_tip_r19_{before,fold,adapter_ro,20260924}.json`
- `data/freeze_manifests/codigo_vivo_tip_r19_100pct_20260924_154857.json` (+ LATEST)
- `data/freeze_manifests/tip_moe_verifier_polish_r19_100pct_20260924_144642.json` (side polish retained)
- `docs/FRONTIER-CODIGO-VIVO-TIP-R19.md` (this file)

Fold SHA: `PENDING` · Base tip: `9c320cb` · Side: `864f5b2` / `f20e327`

R20+ not folded. Tip vis stays BASE. RO `data/lora_adapter/`.
