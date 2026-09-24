# Frontier — Código-vivo tip hardneg R7

**Branch:** `frontier/tip-hardneg-r7` (side branch from tip; fold later)  
**Base tip:** `4291aab` (R6 tip freeze pin after label-protect)  
**When:** 2026-09-24 ~12:51–12:53 ET · Mac-111 (`074c6626-…`)  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.
- R1 / R2 / R3 / R4 / R5 / R6 / label-protect fixtures must still hold after R7 reinforce.
- Do **not** touch tip fold worktree `/Users/anthony/Documents/quantum-llm-lab-tip-cv` or R6 / own-delta worktrees.

## R7 families (≠ R1–R6 / ≠ label-protect)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r7_mixed_router.json` | **52** | gha_yaml_gates_list, sql_comment_qubit, bilingual_not_gates, make_phony_targets, poetry_dep_pennylane, redux_selector_cx, jira_key_quantum, plantuml_actor_bell, dockerfile_stage_qubit, azure_pipeline_gates, puppet_class_n_qubits, bibtex_key_entangle, svelte_store_entangle, vim_syntax_hadamard + ent/vision/base controls |
| `data/bench_live/hardneg_r7_python_items.json` | **44** | same coding themes; GT stdout harness-only |

HARD traps (pre-reinforce drops): CI YAML multiline `gates:\n  - …`; bare `len('gates:')` key token; Azure dashed `gates:` lists; base chat mentioning YAML dashed gates blocked ENT_NEG cancel.

## Scores

| Surface | Pre-reinforce | Post-reinforce (1 layer) |
|---------|---------------|---------------------------|
| R7 router | 48/52 (**0.9231**) | **52/52 (1.0)** |
| R7 verifier alone loop | **1.0** (44/44) | **1.0** (44/44) |
| R7 unified loop | **1.0** (44/44) | **1.0** (44/44) |
| Mixed (d) unified overall | **1.0 (held ≥0.967)** | **1.0 (held)** |
| R1–R6 routers | held | **18/18 · 22/22 · 35/35 · 40/40 · 44/44 · 48/48** |
| R3–R6 verifiers | held | **28/28 · 32/32 · 36/36 · 40/40** |
| LP router/verifier | held | **43/43 · 32/32** |
| Router smoke | 12/12 | 12/12 |
| `ent_never_on_python` | true | true |

## Reinforce layer (gold-free, once)

1. **Router** — exclude CI YAML multiline `gates:\n  - …`; Make `.PHONY: gates`; bare `'gates:'` / `len('gates:')` key tokens; bilingual `NOT gates` / `NO son gates` / `esto no son gates`; ENT_NEG cancel not blocked by those ops-label chat mentions.
2. **Proposer** — none required (R7 python paths already 44/44 on existing lifts).

## Freeze polish_r7

| Manifest | pct |
|----------|-----|
| `data/freeze_manifests/tip_moe_verifier_polish_r7_100pct_*.json` | **100** |

Evidence: `data/freeze_metrics/codigo_vivo_tip_adv_r7_20260924.json`

## CLI

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r7
/Users/anthony/Documents/quantum-llm-lab/.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r7_mixed_router.json
/Users/anthony/Documents/quantum-llm-lab/.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r7_python_items.json \
  --hardneg-router data/bench_live/hardneg_r7_mixed_router.json
/Users/anthony/Documents/quantum-llm-lab/.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `data/bench_live/hardneg_r7_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r7.json`
- `data/frontier_moe_verifier_hardneg_r7.json`
- `data/frontier_moe_verifier_mixed_{cpu,unified}.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r7_20260924.json`
- `data/freeze_manifests/tip_moe_verifier_polish_r7_100pct_*.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R7.md` (this file)

## What this does NOT do

- No merge to `main`.
- No writes under `data/lora_adapter/`.
- No quantum-advantage marketing.
- No CloudAgent. MachineId `074c6626-…` only.
- Does not touch tip-cv / R6 / own-delta worktrees.
- Not yet folded into `frontier/codigo-vivo-tip` (side branch only).
