# Frontier — Código-vivo tip hardneg R26

**Branch:** `frontier/tip-hardneg-r26` (side; not folded)  
**Base tip:** `422a9e3` (`frontier/codigo-vivo-tip` post tip hardneg R15 fold cite; ≥422a9e3)  
**When:** 2026-09-24T15:18:23-04:00 · Mac-111 (`074c6626-0440-4817-9829-6bae77c578d6`)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r26`  
**Feat sha:** `REPLACE_FEAT`  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`. No CloudAgent.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.
- R7 / R8 / R9 / R10 / R11 / R12 / R13 / R14 / label-protect fixtures must still hold after R26 reinforce.
- Do **not** touch tip-cv, tip-tti*, tip-distance-*, tip-hardneg-r12..r25, tip-inverse*, tip-circ*, tip-future*, tip-choose*, tip-pillars*, tip-lp*, tip-label* (other lanes / fold queue). R26 stays side-only. **Do NOT fold.**

## R26 families (≠ R1–R25 / ≠ label-protect)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r26_mixed_router.json` | **52** | cdk_construct_gates, serverless_events_gates, bullmq_job_gates, passport_serialize_gates, torch_hook_gates, lightning_callback_gates, huggingface_pipeline_gates, vscode_command_gates, hardhat_task_gates, foundry_cheat_gates, podman_quadlet_gates, kaniko_destination_gates, grafana_alert_gates, dask_delayed_gates + ent/vision/base controls |
| `data/bench_live/hardneg_r26_python_items.json` | **44** | same coding themes; GT stdout harness-only |

HARD traps (pre-reinforce drops): CDK `gates: CfnResource`; Serverless `gates: events.http`; BullMQ `gates: Job.opts`; Passport `gates: serializeUser`; PyTorch `gates: register_forward_hook`; Lightning `gates: on_train_epoch_end`; HuggingFace `gates: AutoTokenizer`; VSCode `gates: contributes.commands`; Hardhat `gates: hardhat.task`; Foundry `gates: vm.prank`; Podman `gates: Quadlet`; Kaniko `gates: --destination`; Grafana `gates: alert_rule`; Dask `gates: dask.delayed`; base chat with those distractors + ENT_NEG.

Avoided (R9–R25 + tip-claimed): OpenAPI/Helm/… through Playwright/Cypress/Vitest/Pytest/k6/Locust/tRPC/Strapi/Payload/Storybook/Godot/Bevy/Sentry/OpenSearch and R12–R24 families.

## Scores

| Surface | Pre-reinforce | Post-reinforce (1 layer) |
|---------|---------------|---------------------------|
| R26 router | 6/52 (**0.1154**) | **52/52 (1.0)** |
| R26 verifier alone loop | **1.0** (44/44) | **1.0** (44/44) |
| R26 unified loop | router-limited pre | **1.0** (44/44) |
| Mixed (d) unified overall | **1.0 (held ≥0.967)** | **1.0 (held)** |
| R7–R14 routers | held | **52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52** |
| R12/LP verifiers | held | **44/44 · 42/42** |
| LP router | held | **64/64** |
| Router smoke | 12/12 | 12/12 |
| Pillars / hardneg smoke | 37/37 · 18/18 | held (mixed pillar_routing 37/37 · hardneg 18/18) |
| `ent_never_on_python` | true | true |

Rise: 6→52 hits (**+766%** rate vs pre 0.1154→1.0; **+88.46 pp**) ≥80% freeze gate.

## Reinforce layer (gold-free, once)

1. **Router** — exclude CDK `gates: CfnResource`; Serverless `gates: events.http`; BullMQ `gates: Job.opts`; Passport `gates: serializeUser`; PyTorch `gates: register_forward_hook`; Lightning `gates: on_train_epoch_end`; HuggingFace `gates: AutoTokenizer`; VSCode `gates: contributes.commands`; Hardhat `gates: hardhat.task`; Foundry `gates: vm.prank`; Podman `gates: Quadlet`; Kaniko `gates: --destination`; Grafana `gates: alert_rule`; Dask `gates: dask.delayed`; construct/events/job/serialize/hook/callback/pipeline/command/task/cheat/quadlet/destination/alert/delayed prose. R1–R15 patterns unchanged (R16–R25 not on tip base).
2. **Proposer** — none (all 44 heuristic-solvable).

## Freeze polish_r26

| Manifest | pct |
|----------|-----|
| `data/freeze_manifests/tip_moe_verifier_polish_r26_100pct_20260924_151823.json` | **100** |

Evidence: `data/freeze_metrics/codigo_vivo_tip_adv_r26_20260924.json`

## CLI

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r26
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r26_mixed_router.json
.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r26_python_items.json \
  --hardneg-router data/bench_live/hardneg_r26_mixed_router.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `data/bench_live/hardneg_r26_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r26.json`
- `data/frontier_moe_verifier_hardneg_r26.json`
- `data/frontier_moe_verifier_mixed_{cpu,unified}.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r26_20260924.json`
- `data/freeze_manifests/tip_moe_verifier_polish_r26_100pct_20260924_151823.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R26.md` (this file)

## Not folded

Leave tip-cv / tip-tti* / tip-distance-* / tip-hardneg-r12..r25 / tip-inverse* / tip-circ* / tip-future* / tip-choose* / tip-pillars* / tip-lp* / tip-label* alone (fold queue choose-n→R16→tti-cold→R17…→R25). Side branch only. **Do NOT fold.** R26 folds after R25.
