# FRONTIER — Código-vivo tip label-protect-expand

**Status:** **FOLDED** into `frontier/codigo-vivo-tip`  
**Branch (side):** `frontier/tip-label-protect-expand`  
**Fold worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-cv` (Mac-111)  
**Base tip (fold):** `f0dfb11` (post pillars-reinforce)  
**Side base tip:** `8beae21` · **Feat SHA (side):** `5890883`  
**Side tip pin:** `f2b5031`  
**When (side):** 2026-09-24 ~14:47–14:50 ET · **Fold:** 2026-09-24 15:03:06 ET  
**Side freeze:** `codigo_vivo_tip_label_protect_expand_100pct_20260924_145044`  
**Fold freeze:** `codigo_vivo_tip_label_protect_expand_fold_100pct_20260924_150306`  
**Fold feat SHA:** `PENDING`  
**Claim:** NO quantum advantage. Expand + reinforce fall/super **domain label** protect coverage; tip vis stays BASE.

## SHA / setup

| Field | Value |
|-------|-------|
| Tip base SHA (fold) | `f0dfb11` |
| Side feat SHA | `5890883` |
| Side tip pin | `f2b5031` |
| Fold branch | `frontier/codigo-vivo-tip` |
| Host | Mac-111 |
| Model | `mlx-community/Qwen3-VL-8B-Thinking-4bit` |
| Adapters | **READ-ONLY** (`ro_mtime_unchanged=true`) |
| Fold into tip | **true** |

## Why

Tip LP sat at **43/43 · 32/32**. Coverage gaps (`domain label` / `domain_label` taxonomy chat stealing ent via `ENT_RE`, `/v1/domain-labels` tax API + `Reply JSON`, empty `gates=[]` docs-only without `No circuit`, English `NOT valid JSON` / `Do not reply with valid JSON`) were not in the bench. Side added **+21** router / **+10** python cases; fold merge-ports those onto post-pillars tip and re-smokes **64/64 · 42/42**.

## Coverage before → after (fold re-smoke)

| | tip before (post pillars) | tip after fold |
|--|---------------------------|----------------|
| LP router | **43/43** | **64/64** |
| LP verifier | **32/32** | **42/42** |
| Side trail | 43→64 · 32→42 | (+21 / +10) |
| Mixed (d) unified | **1.0** | **1.0** held |
| Pillars | **37/37** | **37/37** retained |
| Circ axis | **5/5** | **5/5** retained |
| `ent_never_on_python` | true | true |
| R13 / R12 / R5 / R7 | 52/52 · 52/52 · 44/44 · 52/52 | **held** |

## New LP families (+21 router)

| family | n | tip miss mode |
|--------|---|---------------|
| `domain_label_chat` | 4 | `domain label` chat → ent via `ENT_RE` |
| `domain_label_snake_cfg` | 3 | `domain_label=` config/env → ent |
| `tax_api_domain_labels` | 3 | `/v1/domain-labels` + Reply JSON blocks ENT_NEG |
| `gates_empty_docs_tax` | 3 | `gates=[]` + fall docs-only (bare `gates` ENT_RE) |
| `neg_valid_json_en` | 3 | English valid-JSON negation + domain label |
| `qubit_metaphor_tax` | 2 | qubit metaphor + domain label chat |
| `ent_control_domain_label` | 3 | real JSON circuit asks with domain/label **stay ent** |

## Router reinforce (RO adapters)

1. **LP tax cancel** — `domain label` / `domain_label` without real `ent_json_ask` cancels bare ENT_RE.
2. **Tax API** — `/v1/domain-labels` / taxonomy API in `schema_field_distract`; ENT_NEG cancel allowed with reply-json tax paths.
3. **gates_ops_label + docs/taxonomy** — empty gates docs-only cancels bare `gates` steal.
4. **English valid-JSON negation** — `Do not reply with valid JSON` / `NOT valid JSON` / `never emit valid JSON`.

**Kept from pillars fold:** `PYTHON_RE` extras / no-python disclaimer / quantum-gates-vs-ops; circ `vis_circ_*` routing extras.

## Anti-contam

| Check | Result |
|-------|--------|
| `prompt_touches_gt` | **false** |
| writes to `data/lora_adapter/` | **false** |
| `ro_mtime_unchanged` | **true** |
| tip vis pillar | **BASE** |
| merge main | **no** |
| fold into tip | **yes** |
| R14+ folded | **no** |

## Freeze?

**YES.** Clear rise **43→64** (100%) **and** verifier **42/42** **and** mixed 1.0 **and** pillars 37/37 **and** circ 5/5 **and** R13/R12/R5/R7 held.

## Reproduce

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-cv
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
unset PYTHONPATH
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_label_protect_mixed_router.json
.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_label_protect_python_items.json \
  --hardneg-router data/bench_live/hardneg_label_protect_mixed_router.json
.venv/bin/python examples/moe_verifier_mixed_live.py --smoke
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## What this does NOT do

- Touch `data/lora_adapter/`
- Merge main
- Fold R14+ / choose-n / tti-cold / R15…R23
