# Frontier — Código-vivo tip hardneg R11

**Status:** **FOLDED** into `frontier/codigo-vivo-tip` (cherry-pick rebase `6bb06fc`/`8764220` onto `f70faa1` → content `4629919` / pin `e472522` FF-equivalent)  
**Branch:** `frontier/tip-hardneg-r11` (rebased; source kept) · tip `frontier/codigo-vivo-tip`  
**Base tip at fold:** `f70faa1` (post motion-r4) · R11 originally from `1304d1a`  
**When:** polish ~13:51 ET · fold 2026-09-24 14:07:23 ET · Mac-111 (`074c6626-…`)  
**Freeze:** `codigo_vivo_tip_r11_100pct_20260924_140723`  
**Worktree (fold):** `/Users/anthony/Documents/quantum-llm-lab-tip-cv` (tip ONLY)  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`. No CloudAgent.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.
- R1 / R2 / R3 / R4 / R5 / R6 / R7 / R8 / R9 / R10 / label-protect fixtures must still hold after R11 reinforce.
- Folded on tip-cv only; retain motion_r4 / vision_ground / inverse_r2 / r10 + priors. Do **not** fold distance-mid / TTI here.

## R11 families (≠ R1–R10 / ≠ label-protect)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r11_mixed_router.json` | **52** | smithy_member_gates, prisma_field_gates, ansible_var_gates, consul_intention_gates, linkerd_server_gates, cilium_policy_gates, airflow_task_gates, kafka_acl_gates, prometheus_relabel_gates, kyverno_validate_gates, gradle_property_gates, zig_comptime_gates, dart_annotation_gates, temporal_activity_gates + ent/vision/base controls |
| `data/bench_live/hardneg_r11_python_items.json` | **44** | same coding themes; GT stdout harness-only |

HARD traps (pre-reinforce drops): Smithy `gates: Long|Boolean`; Ansible `gates: yes` / `gates: "{{`; Linkerd `gates: inbound`; Cilium `gates: toEntities|toCIDR`; Airflow `gates: branch_*`; Kafka `gates: Describe`; Prometheus `gates: replacement`; Kyverno `gates: Audit`; Temporal `gates: ActivityOptions`; base chat with those distractors + ENT_NEG.

Avoided (R9/R10): OpenAPI/Helm/Pulumi/… and AsyncAPI/Nomad/Vault/Istio/ArgoCD/Tekton/FlatBuffers/Cap'n/Solidity/Rust cfg/Kotlin/csproj/SPARQL/Cypher/Earthfile.

## Scores

| Surface | Pre-reinforce | Post-reinforce (1 layer) |
|---------|---------------|---------------------------|
| R11 router | 21/52 (**0.4038**) | **52/52 (1.0)** |
| R11 verifier alone loop | **1.0** (44/44) | **1.0** (44/44) |
| R11 unified loop | 17/44 (router-limited) | **1.0** (44/44) |
| Mixed (d) unified overall | **1.0 (held ≥0.967)** | **1.0 (held)** |
| R1–R10 routers | held | **18/18 · 22/22 · 35/35 · 40/40 · 44/44 · 48/48 · 52/52 · 52/52 · 52/52 · 52/52** |
| R3–R10 verifiers | held | **28/28 · 32/32 · 36/36 · 40/40 · 44/44 · 44/44 · 44/44 · 44/44** |
| LP router/verifier | held | **43/43 · 32/32** |
| Router smoke | 12/12 | 12/12 |
| `ent_never_on_python` | true | true |

## Reinforce layer (gold-free, once)

1. **Router** — exclude Smithy `gates: Long|Boolean`; Ansible `gates: yes` / `gates: "{{`; Linkerd `gates: inbound`; Cilium `gates: toEntities|toCIDR`; Airflow `gates: branch_*` / task_id; Kafka ACL `gates: Describe`; Prometheus relabel `gates: replacement`; Kyverno `gates: Audit`; Temporal `gates: ActivityOptions`; IDL/YAML/mesh-proxy/eBPF/DAG/broker/scrape/policy/orchestration prose. R1–R10 patterns unchanged.
2. **Proposer** — none (all 44 heuristic-solvable).

## Freeze polish_r11

| Manifest | pct |
|----------|-----|
| `data/freeze_manifests/tip_moe_verifier_polish_r11_100pct_20260924_135200.json` | **100** |

Evidence: `data/freeze_metrics/codigo_vivo_tip_adv_r11_20260924.json`

## CLI

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r11
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r11_mixed_router.json
.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r11_python_items.json \
  --hardneg-router data/bench_live/hardneg_r11_mixed_router.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `data/bench_live/hardneg_r11_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r11.json`
- `data/frontier_moe_verifier_hardneg_r11.json`
- `data/frontier_moe_verifier_mixed_{cpu,unified}.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r11_20260924.json`
- `data/freeze_manifests/tip_moe_verifier_polish_r11_100pct_20260924_135200.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R11.md` (this file)

## Fold re-smoke (2026-09-24 14:07:23 ET)

| Surface | Result |
|---------|--------|
| R11 router / verifier | **52/52 · 44/44** |
| mixed (d) unified | **1.0** |
| motion known coverage (n=200) | **100%** (141 ind + 59 corr) |
| scene_0222 | **independent** |
| vision BASE | **1.000** (10/10) · circ **2/2** |
| inverse_cv | **99.82%** |
| collision physics | **100%** (n=40 / 2850) |
| choose_safest | **100%** |
| R10 | **52/52 · 44/44** |
| pillars / hardneg smoke | **26/26 · 18/18** |
| adapters RO | **held** |

## What this does NOT do

- Folded into tip; no merge to `main`.
- No `lora_adapter` writes.
- No CloudAgent. Tip worktree ONLY at fold time.
- Does **not** fold distance-mid / TTI (next folds).
- No quantum-advantage marketing.
