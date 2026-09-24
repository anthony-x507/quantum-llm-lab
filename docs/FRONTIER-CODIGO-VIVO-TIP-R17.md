# Frontier — Código-vivo tip hardneg R17

**Branch:** `frontier/tip-hardneg-r17` → **FOLDED** into `frontier/codigo-vivo-tip`  
**Side:** `970fc4a` / feat `297fba1` · **Base tip:** `a54b74c` (post tti-cold fold)  
**When:** polish side ~14:34–14:36 ET · fold 2026-09-24 15:39:21 ET · Mac-111 (`074c6626-…`)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-cv`  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`. No CloudAgent.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.
- R2–R16 / label-protect / choose_n / tti-cold / pillars / circ fixtures must still hold after R17 fold.
- Do **not** fold R18+ in this task. Do **not** reopen tti-cold residual chase.

## R17 families (≠ R1–R16 / ≠ label-protect)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r17_mixed_router.json` | **52** | cloudflare_worker_gates, cloudfront_behavior_gates, vitess_vschema_gates, cockroach_grant_gates, pinot_table_gates, circleci_when_gates, drone_when_gates, maven_profile_gates, sbt_task_gates, rails_before_action_gates, phoenix_plug_gates, flagger_canary_gates, argorollouts_step_gates, debezium_filter_gates + ent/vision/base controls |
| `data/bench_live/hardneg_r17_python_items.json` | **44** | same coding themes; GT stdout harness-only |

HARD traps: Cloudflare Worker `gates: fetch`; CloudFront `gates: PathPattern`; Vitess `gates: sharded`; CockroachDB `gates: GRANT`; Pinot `gates: ingestion`; CircleCI `gates: equal`; Drone CI `gates: event`; Maven `gates: activeByDefault`; sbt `gates: dependsOn`; Rails `gates: before_action`; Phoenix `gates: plug`; Flagger `gates: stepWeight`; Argo Rollouts `gates: setWeight`; Debezium `gates: op`; base chat with those distractors + ENT_NEG.

## Scores

| Surface | Tip before (no R17 gates) | Tip after fold |
|---------|---------------------------|----------------|
| R17 router | 8/52 (**0.1538**) | **52/52 (1.0)** |
| R17 verifier alone / unified | **44/44** | **44/44 (1.0)** |
| Mixed (d) unified overall | **1.0** | **1.0 (held)** |
| R16 / R15 routers | held | **52/52 · 52/52** |
| LP router/verifier | held | **64/64 · 42/42** |
| Pillars / hardneg smoke / circ | held | **37/37 · 18/18 · 5/5** |
| choose_safest n=80 freeze | retained | **100% @ n=80** retained |
| tti-cold freeze | retained | **~95%** retained (no residual chase) |
| `ent_never_on_python` | true | true |

Side trail: 8→52. Tip rise retention vs side: **44/44 = 100% ≥ 80%** freeze gate.

## Fold re-smoke (2026-09-24 15:39:21 ET)

Cherry-pick `297fba1` onto tip `a54b74c`. Conflicts: STATUS+mixed/LP/r7–r12 JSON ours; router/verifier merged R12+R13+R14+R15+R16+R17 gates_ops.

Freeze: `codigo_vivo_tip_r17_100pct_20260924_153921`

## Artifacts

- `data/bench_live/hardneg_r17_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r17.json`
- `data/frontier_moe_verifier_hardneg_r17.json`
- `data/frontier_moe_verifier_mixed_{cpu,smoke,unified}_r17_fold.json`
- `data/freeze_metrics/codigo_vivo_tip_r17_{before,before_detail,fold,adapter_ro,20260924}.json`
- `data/freeze_manifests/codigo_vivo_tip_r17_100pct_20260924_153921.json` (+ LATEST)
- `data/freeze_manifests/tip_moe_verifier_polish_r17_100pct_20260924_143628.json` (side polish retained)
- `docs/FRONTIER-CODIGO-VIVO-TIP-R17.md` (this file)

## Not folded

R18 @ `1be50d2` → … → R27. tti-cold residual not reopened.
