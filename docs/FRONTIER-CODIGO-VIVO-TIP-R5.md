# Frontier — Código-vivo tip hardneg R5

**Branch:** `frontier/codigo-vivo-tip` (folded from `frontier/tip-hardneg-r5`)  
**Base tip:** `b1c7091` (post_polish) · R5 rebased from `0a1ef4d` · polish `9a12fbc` → `49d7ccc` / pin `55bdfb7`  
**When:** 2026-09-24 ~12:28–12:32 ET · Mac-111 (`074c6626-…`)  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.
- R1 / R2 / R3 / R4 fixtures must still hold after R5 reinforce.

## R5 families (≠ R1 / ≠ R2 / ≠ R3 / ≠ R4)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r5_mixed_router.json` | **44** | k8s_label_qubit, prometheus_metric_cx, graphql_field_entangle, terraform_resource_quantum, jwt_claim_n_qubits, makefile_target_bell, css_class_qubit, protobuf_message_circuit, redis_key_gates, npm_package_cx, xpath_qubit, ansible_role_pennylane + ent/vision/base controls |
| `data/bench_live/hardneg_r5_python_items.json` | **36** | same coding themes; GT stdout harness-only |

HARD traps (pre-reinforce drops): `gates=[cleanup,nightly]` K8s annotation; Helm `gates: [cleanup]`; protobuf `repeated Gate gates = 2;`; Redis key `gates:session:42`; base chat mentioning `gates=[cleanup]` blocked ENT_NEG cancel; XPath `len("//…")` proposer miss.

## Scores

| Surface | Pre-reinforce | Post-reinforce (1 layer) |
|---------|---------------|---------------------------|
| R5 router | 39/44 (**0.8864**) | **44/44 (1.0)** |
| R5 verifier alone loop | **0.9722** (35/36) | **1.0** (36/36) |
| R5 unified loop | **0.96875** (31/32 routed) | **1.0** (36/36) |
| Mixed (d) unified overall | **1.0 (held ≥0.967)** | **1.0 (held)** |
| R1 router | 18/18 | **18/18 (held)** |
| R2 router | 22/22 | **22/22 (held)** |
| R3 router | 35/35 | **35/35 (held)** |
| R3 verifier loop | 28/28 | **28/28 (held)** |
| R4 router | 40/40 | **40/40 (held)** |
| R4 verifier loop | 32/32 | **32/32 (held)** |
| Router smoke | 12/12 | 12/12 |
| `ent_never_on_python` | true | true |

## Reinforce layer (gold-free, once)

1. **Router** — exclude nonempty `gates=[…]` / `gates: […]` k8s/helm allow-lists; Redis `gates:session:…` key paths; protobuf `gates = N;` / `repeated Gate gates =`; ENT_NEG cancel not blocked by ops-label `gates=[…]`.
2. **Proposer** — `len("…")` double-quoted string lift (XPath).

## Freeze polish_r5

| Manifest | pct |
|----------|-----|
| `data/freeze_manifests/tip_moe_verifier_polish_r5_100pct_*.json` | **100** |

Evidence: `data/freeze_metrics/codigo_vivo_tip_adv_r5_20260924.json`

## CLI

```bash
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r5_mixed_router.json
.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r5_python_items.json \
  --hardneg-router data/bench_live/hardneg_r5_mixed_router.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `data/bench_live/hardneg_r5_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r5.json`
- `data/frontier_moe_verifier_hardneg_r5.json`
- `data/frontier_moe_verifier_mixed_{cpu,unified}.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r5_20260924.json`
- `data/freeze_manifests/tip_moe_verifier_polish_r5_100pct_*.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R5.md` (this file)

## FOLDED into tip

**When:** 2026-09-24 12:35:26 ET · Mac-111 (`074c6626-…`)  
**Tip after FF:** `55bdfb7` (rebase onto `b1c7091` + FF). Fold commit follows with scoreboard/STATUS.  
**Prior freezes retained (not abandoned):** platform `f0da3e7`, MLX+R3 `5c67267`, polish_r4 `40f1d7c`, **post_polish** `bf58743` / `codigo_vivo_tip_post_polish_100pct_20260924_123210`, polish_r5 `9a12fbc`.  
**Re-smoke:** mixed (d) **1.0**; R1–R5 routers **18/18 · 22/22 · 35/35 · 40/40 · 44/44**; R3/R4/R5 verifier **28/28 · 32/32 · 36/36**; `wired_to_vlm=true`; `ent_never_on_python=true`.

## What this does NOT do

- No merge to `main`.
- No writes under `data/lora_adapter/`.
- No quantum-advantage marketing.
- No CloudAgent. MachineId `074c6626-…` only.
- Folded into `frontier/codigo-vivo-tip`; source branch kept for history.
