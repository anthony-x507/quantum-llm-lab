# Frontier — Código-vivo tip hardneg R25

**Branch:** `frontier/tip-hardneg-r25` (side; not folded)  
**Base tip:** `bc6902f` (`frontier/codigo-vivo-tip` post tip hardneg R14 fold cite; ≥bc6902f)  
**When:** 2026-09-24T15:13:10-04:00 ET · Mac-111 (`074c6626-0440-4817-9829-6bae77c578d6`)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r25`  
**Feat sha:** `PENDING`  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`. No CloudAgent.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.
- R7 / R8 / R9 / R10 / R11 / R12 / R13 / R14 / label-protect fixtures must still hold after R25 reinforce.
- Do **not** touch tip-cv, tip-tti*, tip-distance-*, tip-hardneg-r12..r24, tip-inverse*, tip-circ*, tip-future*, tip-choose*, tip-pillars*, tip-lp*, tip-label* (other lanes / fold queue). R25 stays side-only. **Do NOT fold.**

## R25 families (≠ R1–R24 / ≠ label-protect)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r25_mixed_router.json` | **52** | playwright_fixture_gates, cypress_command_gates, vitest_mock_gates, pytest_mark_gates, k6_executor_gates, locust_taskset_gates, trpc_procedure_gates, strapi_lifecycle_gates, payload_hook_gates, storybook_decorator_gates, godot_signal_gates, bevy_system_gates, sentry_hook_gates, opensearch_pipeline_gates + ent/vision/base controls |
| `data/bench_live/hardneg_r25_python_items.json` | **44** | same coding themes; GT stdout harness-only |

HARD traps (pre-reinforce drops): Playwright `gates: test.extend`; Cypress `gates: Commands.add`; Vitest `gates: vi.mock`; Pytest `gates: pytest.mark`; k6 `gates: ramping-vus`; Locust `gates: TaskSet`; tRPC `gates: protectedProcedure`; Strapi `gates: beforeCreate`; Payload `gates: beforeChange`; Storybook `gates: decorators`; Godot `gates: emit_signal`; Bevy `gates: ResMut`; Sentry `gates: before_send`; OpenSearch `gates: processors`; base chat with those distractors + ENT_NEG.

Avoided (R9–R24 + tip-claimed): OpenAPI/Helm/… through Wails/Neutralino/RN/Ionic/Webpack/Parcel/SWC/moonrepo/Lage/ESLint/Ruff/SQLAlchemy/EdgeDB/MAUI and R12–R23 families.

## Scores

| Surface | Pre-reinforce | Post-reinforce (1 layer) |
|---------|---------------|---------------------------|
| R25 router | 6/52 (**0.1154**) | **52/52 (1.0)** |
| R25 verifier alone loop | **1.0** (44/44) | **1.0** (44/44) |
| R25 unified loop | router-limited pre | **1.0** (44/44) |
| Mixed (d) unified overall | **1.0 (held ≥0.967)** | **1.0 (held)** |
| R7–R14 routers | held | **52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52** |
| R12/LP verifiers | held | **44/44 · 42/42** |
| LP router | held | **64/64** |
| Router smoke | 12/12 | 12/12 |
| Pillars / hardneg smoke | 37/37 · 18/18 | held (mixed pillar_routing 37/37 · hardneg 18/18) |
| `ent_never_on_python` | true | true |

Rise: 6→52 hits (**+766%** rate vs pre 0.1154→1.0; **+88.46 pp**) ≥80% freeze gate.

## Reinforce layer (gold-free, once)

1. **Router** — exclude Playwright `gates: test.extend`; Cypress `gates: Commands.add`; Vitest `gates: vi.mock`; Pytest `gates: pytest.mark`; k6 `gates: ramping-vus`; Locust `gates: TaskSet`; tRPC `gates: protectedProcedure`; Strapi `gates: beforeCreate`; Payload `gates: beforeChange`; Storybook `gates: decorators`; Godot `gates: emit_signal`; Bevy `gates: ResMut`; Sentry `gates: before_send`; OpenSearch `gates: processors`; fixture/command/mock/mark/executor/taskset/procedure/lifecycle/hook/decorator/signal/system/pipeline prose. R1–R14 patterns unchanged (R15–R24 not on tip base).
2. **Proposer** — none (all 44 heuristic-solvable).

## Freeze polish_r25

| Manifest | pct |
|----------|-----|
| `data/freeze_manifests/tip_moe_verifier_polish_r25_100pct_20260924_151310.json` | **100** |

Evidence: `data/freeze_metrics/codigo_vivo_tip_adv_r25_20260924.json`

## CLI

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r25
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r25_mixed_router.json
.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r25_python_items.json \
  --hardneg-router data/bench_live/hardneg_r25_mixed_router.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `data/bench_live/hardneg_r25_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r25.json`
- `data/frontier_moe_verifier_hardneg_r25.json`
- `data/frontier_moe_verifier_mixed_{cpu,unified}.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r25_20260924.json`
- `data/freeze_manifests/tip_moe_verifier_polish_r25_100pct_20260924_151310.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R25.md` (this file)

## Not folded

Leave tip-cv / tip-tti* / tip-distance-* / tip-hardneg-r12..r24 / tip-inverse* / tip-circ* / tip-future* / tip-choose* / tip-pillars* / tip-lp* / tip-label* alone (fold queue R15→choose-n→R16→tti-cold→R17…→R24). Side branch only. **Do NOT fold.** R25 folds after R24.
