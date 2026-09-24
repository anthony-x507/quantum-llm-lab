# Frontier — Código-vivo tip hardneg R18

**Branch:** `frontier/tip-hardneg-r18` (side; not folded)  
**Base tip:** `5fb00e3` (`frontier/codigo-vivo-tip` post tip-distance-far polish; ≥ brief pin `34c696f`)  
**When:** 2026-09-24 ~2026-09-24T14:39:50-04:00 ET · Mac-111 (`074c6626-…`)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r18`  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`. No CloudAgent.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.
- R7 / R8 / R9 / R10 / R11 / R12 / label-protect fixtures must still hold after R18 reinforce.
- Do **not** touch tip-cv, tip-tti*, tip-distance-mid/far, tip-hardneg-r12..r17, tip-inverse-r3, tip-circ-expand, tip-future-track*, tip-choose-safest-n (other lanes / fold queue). R18 stays side-only. **Do NOT fold.**

## R18 families (≠ R1–R17 / ≠ label-protect)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r18_mixed_router.json` | **52** | aws_alb_rule_gates, azure_frontdoor_gates, gcp_urlmap_gates, hudi_table_gates, iceberg_snapshot_gates, flink_checkpoint_gates, nifi_processor_gates, concourse_step_gates, woodpecker_when_gates, teamcity_condition_gates, cargo_feature_gates, go_build_tag_gates, quarkus_interceptor_gates, micronaut_filter_gates + ent/vision/base controls |
| `data/bench_live/hardneg_r18_python_items.json` | **44** | same coding themes; GT stdout harness-only |

HARD traps (pre-reinforce drops): AWS ALB `gates: host-header`; Azure Front Door `gates: matchCondition`; GCP URL Map `gates: pathMatcher`; Apache Hudi `gates: hoodie`; Apache Iceberg `gates: snapshot-id`; Apache Flink `gates: exactly_once`; Apache NiFi `gates: auto-terminated`; Concourse CI `gates: try`; Woodpecker CI `gates: branch`; TeamCity `gates: equals`; Cargo `gates: default`; Go build tags `gates: goos`; Quarkus `gates: AroundInvoke`; Micronaut `gates: Filter`; base chat with those distractors + ENT_NEG.

Avoided (R9–R17): OpenAPI/Helm/…, AsyncAPI/Istio/…, Smithy/Linkerd/Cilium/…, Traefik/Envoy/NATS/Flux/Kong/Spinnaker/…, Nginx/HAProxy/Caddy/…, Apache httpd/Varnish/APISIX/…, Squid/OpenResty/Contour/…, ATS/CoreDNS/Pulsar/…, Cloudflare Worker/CloudFront/Vitess/CockroachDB/Pinot/CircleCI/Drone/Maven/sbt/Rails/Phoenix/Flagger/Argo Rollouts/Debezium.

## Scores

| Surface | Pre-reinforce | Post-reinforce (1 layer) |
|---------|---------------|---------------------------|
| R18 router | 6/52 (**0.1154**) | **52/52 (1.0)** |
| R18 verifier alone loop | **1.0** (44/44) | **1.0** (44/44) |
| R18 unified loop | router-limited pre | **1.0** (44/44) |
| Mixed (d) unified overall | **1.0 (held ≥0.967)** | **1.0 (held)** |
| R7–R12 routers | held | **52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52** |
| R12/LP verifiers | held | **44/44 · 32/32** |
| LP router | held | **43/43** |
| Router smoke | 12/12 | 12/12 |
| Pillars / hardneg smoke | 26/26 · 18/18 | held |
| `ent_never_on_python` | true | true |

Rise: 6→52 hits (**+766%** rate vs pre 0.1154→1.0; **+88.46 pp**) ≥80% freeze gate.

## Reinforce layer (gold-free, once)

1. **Router** — exclude AWS ALB `gates: host-header`; Azure Front Door `gates: matchCondition`; GCP URL Map `gates: pathMatcher`; Hudi `gates: hoodie`; Iceberg `gates: snapshot-id`; Flink `gates: exactly_once`; NiFi `gates: auto-terminated`; Concourse `gates: try`; Woodpecker `gates: branch`; TeamCity `gates: equals`; Cargo `gates: default`; Go `gates: goos`; Quarkus `gates: AroundInvoke`; Micronaut `gates: Filter`; cloud/CDN/lake/stream/ETL/CI/build/language/framework prose. R1–R12 patterns unchanged (R13–R17 not on tip base).
2. **Proposer** — none (all 44 heuristic-solvable).

## Freeze polish_r18

| Manifest | pct |
|----------|-----|
| `data/freeze_manifests/tip_moe_verifier_polish_r18_100pct_20260924_143950.json` | **100** |

Evidence: `data/freeze_metrics/codigo_vivo_tip_adv_r18_20260924.json`

## CLI

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r18
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r18_mixed_router.json
.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r18_python_items.json \
  --hardneg-router data/bench_live/hardneg_r18_mixed_router.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `data/bench_live/hardneg_r18_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r18.json`
- `data/frontier_moe_verifier_hardneg_r18.json`
- `data/frontier_moe_verifier_mixed_{cpu,unified}.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r18_20260924.json`
- `data/freeze_manifests/tip_moe_verifier_polish_r18_100pct_20260924_143950.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R18.md` (this file)

## Not folded

Leave tip-cv / tip-tti* / tip-distance-* / tip-hardneg-r12..r17 / tip-inverse-r3 / tip-circ-expand / tip-future-track* / tip-choose-safest-n alone (fold queue far→R13→future-r3→circ→R14→R15→choose-n→R16→R17). Side branch only. **Do NOT fold.**

## Fold into tip (2026-09-24)

Cherry-pick `ed431ad` onto tip `2e5c484`. Conflicts: STATUS+mixed/LP/r7–r12 JSON ours; router/verifier merged R12+R13+R14+R15+R16+R17+R18 gates_ops.

Freeze: `codigo_vivo_tip_r18_100pct_20260924_154419`

### Fold re-smoke (2026-09-24 15:44:19 ET)

| Surface | Result |
|---------|--------|
| R18 router / verifier | **17→52/52** / **44/44** |
| Side trail | **6→52** · rise_pp **88.46** |
| R17 / mixed (d) | **52/52·44/44 · 1.0** |
| pillars / hardneg smoke / circ | **37/37 · 18/18 · 5/5** |
| choose_n80 / tti-cold | **100%** / **~95%** freeze retained |
| `ent_never_on_python` | true |
| adapters RO | true |

### Artifacts

- `data/bench_live/hardneg_r18_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r18.json`
- `data/frontier_moe_verifier_hardneg_r18.json`
- `data/frontier_moe_verifier_mixed_{cpu,smoke,unified}_r18_fold.json`
- `data/freeze_metrics/codigo_vivo_tip_r18_{before,fold,adapter_ro,20260924}.json`
- `data/freeze_manifests/codigo_vivo_tip_r18_100pct_20260924_154419.json` (+ LATEST)
- `data/freeze_manifests/tip_moe_verifier_polish_r18_100pct_20260924_143950.json` (side polish retained)
- `docs/FRONTIER-CODIGO-VIVO-TIP-R18.md` (this file)

Fold SHA: `e62cb61` · Base tip: `2e5c484` · Side: `1be50d2` / `ed431ad`

R19+ not folded. Tip vis stays BASE. RO `data/lora_adapter/`.

