# Frontier — Código-vivo tip hardneg R4

**Branch:** `frontier/tip-hardneg-r4` (from tip HEAD; tip occupied by fold)  
**Base tip:** `e680271` (MLX+R3 freeze consolidate)  
**When:** 2026-09-24 ~11:25–11:35 ET · Mac-111 (`074c6626-…`)  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.
- R1 / R2 / R3 fixtures must still hold after R4 reinforce.

## R4 families (≠ R1 / ≠ R2 / ≠ R3)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r4_mixed_router.json` | **40** | yaml_key_qubit, sql_column_bell, docker_image_pennylane, git_ref_entangle, json_schema_prop, csv_header_cx, stack_trace_gate, dataclass_n_qubits, email_subject_quantum, toml_section_qubits, mermaid_text_diagram + ent/vision/base controls |
| `data/bench_live/hardneg_r4_python_items.json` | **32** | same coding themes; GT stdout harness-only |

HARD traps (pre-reinforce drops): `gates=hadamard_cleanup` ops label; schema `reply JSON only` + deprecated `n_qubits` field; ENT_NEG blocked by bare `n_qubits`; comment `not gates=[...]`.

R1/R2/R3 families kept distinct (physics-lookalike / bilingual / cli_flag_quantum / …).

## Scores

| Surface | Pre-reinforce | Post-reinforce (1 layer) |
|---------|---------------|---------------------------|
| R4 router | 37/40 (**0.925**) | **40/40 (1.0)** |
| R4 verifier alone loop | **0.6875** (22/32) | **1.0** (32/32) |
| R4 unified loop | **~0.677** (21/31 routed) | **1.0** (32/32) |
| Mixed (d) unified overall | **1.0 (held ≥0.967)** | **1.0 (held)** |
| R1 router | 18/18 | **18/18 (held)** |
| R2 router | 22/22 | **22/22 (held)** |
| R3 router | 35/35 | **35/35 (held)** |
| R3 verifier loop | 28/28 | **28/28 (held)** |
| Router smoke | 12/12 | 12/12 |
| `ent_never_on_python` | true | true |

## Reinforce layer (gold-free, once)

1. **Router** — exclude ops-config `gates=label` / `gates: []` / `not gates=[...]` / schema property-list from `ent_json_ask`; exclude OpenAPI/schema `reply JSON only` near deprecated `n_qubits` field; ENT_NEG cancel no longer blocked by bare `n_qubits` field mention.
2. **Proposer** — `len('a,b'.split(','))` lift; `from dataclasses import dataclass` + `@dataclass` class + `print(...)` block lift.

## Freeze polish_r4

| Manifest | pct |
|----------|-----|
| `data/freeze_manifests/tip_moe_verifier_polish_r4_100pct_*.json` | **100** |

Evidence: `data/freeze_metrics/codigo_vivo_tip_adv_r4_20260924.json`

## CLI

```bash
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r4_mixed_router.json
.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r4_python_items.json \
  --hardneg-router data/bench_live/hardneg_r4_mixed_router.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `data/bench_live/hardneg_r4_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r4.json`
- `data/frontier_moe_verifier_hardneg_r4.json`
- `data/frontier_moe_verifier_mixed_{cpu,unified}.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r4_20260924.json`
- `data/freeze_manifests/tip_moe_verifier_polish_r4_100pct_*.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R4.md` (this file)

## What this does NOT do

- No merge to `main`.
- No writes under `data/lora_adapter/`.
- No quantum-advantage marketing.
- Does not replace tip `frontier/codigo-vivo-tip` (fold-occupied); lives on `frontier/tip-hardneg-r4`.
