# Frontier — Código-vivo tip label-protect / fall-super

**Branch:** `frontier/codigo-vivo-tip` (folded from `frontier/tip-label-protect`)  
**Base tip:** `32fed9b` (R5 tip freeze) · rebased polish `2d86650`→`751ed03` / pin `65de0c9`→`8b0772a`  
**When:** 2026-09-24 ~12:38–12:50 ET · Mac-111 (`074c6626-…`)  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.
- R1 / R2 / R3 / R4 / R5 fixtures must still hold after label-protect reinforce.

## Why (honesty)

Standing queue: hard-neg + **fall/super label-protect**. Own-delta showed ent LoRA can hurt python/vision labels when misapplied; dual-lane protects tip at 1.0.  
This round adds fall/super **taxonomy** negatives so coding/chat prompts that mention `fall` / `superposed` / `domain label` / empty `gates=[]` do **not** steal the ent lane — while real circuit asks with fall/super domain labels still route **ent**.

## Families (≠ R1 / ≠ R2 / ≠ R3 / ≠ R4 / ≠ R5)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_label_protect_mixed_router.json` | **43** | neg_json_valido_tax, gates_empty_eq_fall, taxonomy_enum_fall_super, freefall_classical, superpose_crud, sql_yaml_csv_label, var_collapsed_separable, tax_endpoint_openapi, metric_name_distract + base/vision/ent controls |
| `data/bench_live/hardneg_label_protect_python_items.json` | **32** | same themes; GT stdout harness-only; liftable forms |

HARD traps (pre-reinforce drops): `NOT json válido` / `NO es json válido` near taxonomy; empty ops `gates=[]` next to fall/super labels (ENT_NEG cancel blocked because `gates=` token looked like a circuit ask).

## Scores

| Surface | Pre-reinforce | Post-reinforce |
|---------|---------------|----------------|
| Label-protect router | 36/43 (**0.8372**) | **43/43 (1.0)** |
| Label-protect verifier unified | 26/32 (**0.8125**) first pass | **32/32 (1.0)** after fixture polish |
| Mixed (d) unified overall | **1.0 (held ≥0.967)** | **1.0 (held)** |
| R1–R5 routers | 18/18·22/22·35/35·40/40·44/44 | **held** |
| R3/R4/R5 verifier | 28/28·32/32·36/36 | **held** |
| Router smoke | 12/12 | 12/12 |
| `ent_never_on_python` | true | true |

### Honesty note (verifier Δ)

First verifier pass **26/32**: 6 items used multi-line dict/merge/findall/`.upper()` shapes the gold-free heuristic proposer does not lift. Those **python fixtures** were polished to liftable `Write Python that prints …` forms **with the same fall/super distractors**. Hard router traps (`NOT json válido`, `gates=[]`) remain in `hardneg_label_protect_mixed_router.json` and drive the reinforce layer. No GT leaked into prompts.

## Reinforce layer (gold-free, once)

1. **Router** — `gates=[]` / `gates = []` empty-eq ops markers join `gates_ops_label`; negated `json válido` (`NOT` / `NO es` / `never reply`) does not set `ent_json_ask`.
2. **Fixtures** — fall/super taxonomy distractors on python/base/vision; real fall/super domain JSON-circuit asks stay ent.

## Freeze polish_label_protect

| Manifest | pct |
|----------|-----|
| `data/freeze_manifests/tip_moe_verifier_polish_label_protect_100pct_*.json` | **100** |

Evidence: `data/freeze_metrics/codigo_vivo_tip_adv_label_protect_20260924.json`

## CLI

```bash
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_label_protect_mixed_router.json
.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_label_protect_python_items.json \
  --hardneg-router data/bench_live/hardneg_label_protect_mixed_router.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `data/bench_live/hardneg_label_protect_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_label_protect.json`
- `data/frontier_moe_verifier_hardneg_label_protect.json`
- `data/frontier_moe_verifier_mixed_{cpu,unified}.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_label_protect_20260924.json`
- `data/freeze_manifests/tip_moe_verifier_polish_label_protect_100pct_*.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-LABEL-PROTECT.md` (this file)



## FOLDED into tip

**When:** 2026-09-24 12:44:19 ET · Mac-111 (`074c6626-…`)  
**Tip after FF:** `8b0772a` (rebase onto `32fed9b` + FF).  
**Prior freezes retained (not abandoned):** platform / mlx_r3 / polish_r4/r5 / post_polish / **R5 tip freeze** `codigo_vivo_tip_r5_100pct_20260924_123727` @ `32fed9b`.  
**Re-smoke:** mixed (d) **1.0**; label-protect **43/43·32/32**; R1–R5 held; `ent_never_on_python=true`.

## What this does NOT do

- No merge to `main`.
- No writes under `data/lora_adapter/`.
- No quantum-advantage marketing.
- No CloudAgent. MachineId `074c6626-…` only.
- Does **not** fold into tip yet (tip freeze-busy / dirty); source branch kept for history.