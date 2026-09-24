# Frontier — Código-vivo tip hardneg R3

**Branch:** `frontier/codigo-vivo-tip`  
**Base tip:** `f0da3e7` (MFV overall 1.0 + scaffold ON + R1/R2 reinforces)  
**When:** 2026-09-24 ~11:15–11:20 ET · Mac-139 (`074c6626-…`)  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.

## R3 families (≠ R1 / ≠ R2)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r3_mixed_router.json` | **35** | cli_flag_quantum, regex_token_distract, http_path_qubit, type_hint_circuit, unittest_assert_bell, logline_hadamard, ascii_diagram_no_image, finance_quantum_leap, env_var_n_qubits, cron_cx_job + ent/vision/base controls |
| `data/bench_live/hardneg_r3_python_items.json` | **28** | same coding themes; GT stdout harness-only |

R1 families kept distinct: physics-lookalike / ent-wording / vision-caption-ambiguous.  
R2 families kept distinct: bilingual / measure-in-comment / vision-words-no-image / ent-metaphor-CRUD / json-looking-physics.

## Scores

| Surface | Pre-reinforce | Post-reinforce (1 layer) |
|---------|---------------|---------------------------|
| R3 router | 33/35 (**0.9429**) — `n_qubits` string / `len('N_QUBITS')` → ent | **35/35 (1.0)** |
| R3 verifier alone loop | **0.643** (18/28) | **1.0** (28/28) |
| R3 unified loop | **0.654** (17/26 routed) | **1.0** (28/28) |
| Mixed (d) unified overall | **1.0 (held ≥0.967)** | **1.0 (held)** |
| R1 router | 18/18 | **18/18 (held)** |
| R2 router | 22/22 | **22/22 (held)** |
| Router smoke | 12/12 | 12/12 |
| `ent_never_on_python` | true | true |

## Reinforce layer (gold-free, once)

1. **Router** — `ent_json_ask` no longer treats bare `n_qubits` / `N_QUBITS` inside strings as a JSON-circuit ask; requires gates=/json-válido or `n_qubits` + JSON-reply intent.
2. **Proposer** — optional `->` return annot on `def` embeds; argparse / `import…\nprint` / assign+print lifts; `print(sum([…]))` + `prints sum([…])`; `len(__import__('re').findall(…))`.

## Freeze polish_r3

| Manifest | pct |
|----------|-----|
| `data/freeze_manifests/tip_moe_verifier_polish_r3_100pct_*.json` | **100** |

Evidence: `data/freeze_metrics/codigo_vivo_tip_adv_r3_20260924.json`

## CLI

```bash
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r3_mixed_router.json
.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r3_python_items.json \
  --hardneg-router data/bench_live/hardneg_r3_mixed_router.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `data/bench_live/hardneg_r3_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r3.json`
- `data/frontier_moe_verifier_hardneg_r3.json`
- `data/frontier_moe_verifier_mixed_{cpu,unified}.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r3_20260924.json`
- `data/freeze_manifests/tip_moe_verifier_polish_r3_100pct_*.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R3.md` (this file)

## What this does NOT do

- No merge to `main`.
- No writes under `data/lora_adapter/`.
- No quantum-advantage marketing.
