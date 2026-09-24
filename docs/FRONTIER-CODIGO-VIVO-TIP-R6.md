# Frontier — Código-vivo tip hardneg R6

**Branch:** `frontier/codigo-vivo-tip` (folded from `frontier/tip-hardneg-r6`)  
**Base tip:** `3b10288` (label-protect freeze) · R6 rebased from `32fed9b` → content `f3fcf1e` / pin `259e4a4`  
**When:** 2026-09-24 ~12:44–12:47 ET · Mac-111 (`074c6626-…`)  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.
- R1 / R2 / R3 / R4 / R5 fixtures must still hold after R6 reinforce.
- Do **not** touch tip fold worktree `/Users/anthony/Documents/quantum-llm-lab-tip-cv` (label-protect fold in progress).

## R6 families (≠ R1 / ≠ R2 / ≠ R3 / ≠ R4 / ≠ R5 / ≠ label-protect)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r6_mixed_router.json` | **48** | github_action_qubit, nginx_location_cx, kafka_topic_bell, systemd_unit_quantum, aws_arn_pennylane, bazel_target_cx, cargo_feature_qubit, html_data_attr_entangle, ldap_dn_qubit, cmake_option_n_qubits, groovy_jenkins_gates, elasticsearch_index_bell, gradle_task_entangle, plist_key_qubit + ent/vision/base controls |
| `data/bench_live/hardneg_r6_python_items.json` | **40** | same coding themes; GT stdout harness-only |

HARD traps (pre-reinforce drops): Bazel `//gates:cleanup`; HTML `data-gates="cleanup,nightly"`; Jenkins/Groovy `gates = 'cleanup'`; base chat mentioning those ops-label forms blocked ENT_NEG cancel.

## Scores

| Surface | Pre-reinforce | Post-reinforce (1 layer) |
|---------|---------------|---------------------------|
| R6 router | 43/48 (**0.8958**) | **48/48 (1.0)** |
| R6 verifier alone loop | **1.0** (40/40) | **1.0** (40/40) |
| R6 unified loop | **1.0** (40/40) | **1.0** (40/40) |
| Mixed (d) unified overall | **1.0 (held ≥0.967)** | **1.0 (held)** |
| R1 router | 18/18 | **18/18 (held)** |
| R2 router | 22/22 | **22/22 (held)** |
| R3 router | 35/35 | **35/35 (held)** |
| R3 verifier loop | 28/28 | **28/28 (held)** |
| R4 router | 40/40 | **40/40 (held)** |
| R4 verifier loop | 32/32 | **32/32 (held)** |
| R5 router | 44/44 | **44/44 (held)** |
| R5 verifier loop | 36/36 | **36/36 (held)** |
| Router smoke | 12/12 | 12/12 |
| `ent_never_on_python` | true | true |

## Reinforce layer (gold-free, once)

1. **Router** — exclude Bazel `//gates:target`; HTML `data-gates=` / `data-gates="…"`; Groovy/Jenkins `gates = '…'` / `gates = "…"` quoted assigns; ENT_NEG cancel not blocked by those ops-label chat mentions.
2. **Proposer** — none required (R6 python paths already 40/40 on existing lifts).

## Freeze polish_r6

| Manifest | pct |
|----------|-----|
| `data/freeze_manifests/tip_moe_verifier_polish_r6_100pct_*.json` | **100** |

Evidence: `data/freeze_metrics/codigo_vivo_tip_adv_r6_20260924.json`

## CLI

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r6
/Users/anthony/Documents/quantum-llm-lab/.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r6_mixed_router.json
/Users/anthony/Documents/quantum-llm-lab/.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r6_python_items.json \
  --hardneg-router data/bench_live/hardneg_r6_mixed_router.json
/Users/anthony/Documents/quantum-llm-lab/.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `data/bench_live/hardneg_r6_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r6.json`
- `data/frontier_moe_verifier_hardneg_r6.json`
- `data/frontier_moe_verifier_mixed_{cpu,unified}.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r6_20260924.json`
- `data/freeze_manifests/tip_moe_verifier_polish_r6_100pct_*.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R6.md` (this file)

## FOLDED into tip

**When:** 2026-09-24 12:49:51 ET · Mac-111 (`074c6626-…`)  
**Tip after FF:** `259e4a4` (rebase onto `3b10288` + FF). Fold commit follows with scoreboard/STATUS.  
**Prior freezes retained (not abandoned):** platform, mlx_r3, post_polish, polish_r5, **R5 tip** `codigo_vivo_tip_r5_100pct_20260924_123727`, **label_protect** `codigo_vivo_tip_label_protect_100pct_20260924_124608`, polish_r6.  
**Re-smoke:** mixed (d) **1.0**; R1–R6 routers **18/18 · 22/22 · 35/35 · 40/40 · 44/44 · 48/48**; R3/R4/R5/R6/LP verifier **28/28 · 32/32 · 36/36 · 40/40 · 32/32**; LP router **43/43**; `ent_never_on_python=true`.

## What this does NOT do

- No merge to `main`.
- No writes under `data/lora_adapter/`.
- No quantum-advantage marketing.
- No CloudAgent. MachineId `074c6626-…` only.
- Folded into `frontier/codigo-vivo-tip`; source branch kept for history.
