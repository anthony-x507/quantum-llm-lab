# Frontier — Código-vivo tip hardneg R16

**Branch:** `frontier/tip-hardneg-r16` → **FOLDED** into `frontier/codigo-vivo-tip`  
**Base tip:** `88287bc` (`origin/frontier/codigo-vivo-tip` post choose-safest-n fold)  
**When:** 2026-09-24 ~15:22 ET · Mac-111 (`074c6626-…`)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-cv`  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`. No CloudAgent.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.
- R1–R15 / label-protect / choose_n / pillars / circ fixtures must still hold after R16 fold.
- Do **not** fold tti-cold / R17+ in this task.

## R16 families (≠ R1–R15 / ≠ label-protect)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r16_mixed_router.json` | **52** | trafficserver_remap_gates, coredns_acl_gates, pulsar_topic_gates, redpanda_acl_gates, github_actions_needs_gates, gitlab_ci_rules_gates, terraform_count_gates, nix_flake_gates, express_mw_gates, flask_before_gates, knative_serving_gates, keda_scaler_gates, dapr_middleware_gates, gatekeeper_constraint_gates + ent/vision/base controls |
| `data/bench_live/hardneg_r16_python_items.json` | **44** | same coding themes; GT stdout harness-only |

HARD traps: ATS `gates: remap`; CoreDNS `gates: acl`; Pulsar `gates: produce`; Redpanda `gates: ALTER`; GitHub Actions `gates: needs`; GitLab CI `gates: rules`; Terraform `gates: count`; Nix flake `gates: outputs`; Express `gates: helmet`; Flask `gates: before_request`; Knative `gates: minScale`; KEDA `gates: cooldownPeriod`; Dapr `gates: Retry`; Gatekeeper `gates: enforcementAction`; base chat with those distractors + ENT_NEG.

## Scores

| Surface | Tip before (no R16 gates) | Tip after fold |
|---------|---------------------------|----------------|
| R16 router | 11/52 (**0.2115**) | **52/52 (1.0)** |
| R16 verifier alone / unified | **44/44** | **44/44 (1.0)** |
| Mixed (d) unified overall | **1.0** | **1.0 (held)** |
| R15 / R14 routers | held | **52/52 · 52/52** |
| LP router/verifier | held | **64/64 · 42/42** |
| Pillars / hardneg smoke / circ | held | **37/37 · 18/18 · 5/5** |
| choose_safest n=80 freeze | retained | **100% @ n=80** retained |
| `ent_never_on_python` | true | true |

Side trail: 6→52. Tip rise retention vs side: **41/46 ≈ 89.1% ≥ 80%** freeze gate.

## Fold re-smoke (2026-09-24 15:22:53 ET)

Cherry-pick `d4eea50` onto tip `88287bc`. Conflicts: STATUS+mixed/LP/r7–r12 JSON ours; router/verifier merged R12+R13+R14+R15+R16 gates_ops + r16 out paths.

Freeze: `codigo_vivo_tip_r16_100pct_20260924_152253`

## Artifacts

- `data/bench_live/hardneg_r16_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r16.json`
- `data/frontier_moe_verifier_hardneg_r16.json`
- `data/frontier_moe_verifier_mixed_{cpu,unified,smoke}_r16_fold.json`
- `data/freeze_metrics/codigo_vivo_tip_r16_{before,before_detail,fold,adapter_ro,20260924}.json`
- `data/freeze_manifests/codigo_vivo_tip_r16_100pct_20260924_152253.json` (+ LATEST)
- `data/freeze_manifests/tip_moe_verifier_polish_r16_100pct_20260924_143253.json` (side polish retained)
- `docs/FRONTIER-CODIGO-VIVO-TIP-R16.md` (this file)

## Not folded

tti-cold / R17+ stay out of this fold.
