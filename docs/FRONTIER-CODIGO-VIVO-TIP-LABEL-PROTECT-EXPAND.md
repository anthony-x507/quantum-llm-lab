# FRONTIER — Código-vivo tip label-protect-expand (side)

**Status:** **SIDE ONLY — NOT FOLDED** into `frontier/codigo-vivo-tip`  
**Branch:** `frontier/tip-label-protect-expand`  
**Base tip:**  · **Feat SHA:** `8beae21` (≥`f052420`; post R13 fold pin)  
**When:** 2026-09-24 ~14:47–14:50 ET · Mac-111 (`074c6626-…`)  
**Claim:** NO quantum advantage. Expand + reinforce fall/super **domain label** protect coverage; tip vis stays BASE.

## SHA / setup

| Field | Value |
|-------|-------|
| Tip base SHA | `8beae21` |
| Branch | `frontier/tip-label-protect-expand` |
| Host | Mac-111 |
| Model | `mlx-community/Qwen3-VL-8B-Thinking-4bit` |
| Adapters | **READ-ONLY** (`ro_mtime_unchanged=true`) |
| Fold into tip | **false** |

## Why

Tip LP sat at **43/43 · 32/32**. Coverage gaps tip currently misses (`domain label` / `domain_label` taxonomy chat stealing ent via `ENT_RE`, `/v1/domain-labels` tax API + `Reply JSON`, empty `gates=[]` docs-only without `No circuit`, English `NOT valid JSON` / `Do not reply with valid JSON`) were not in the bench. This side branch adds **+21** router / **+10** python cases and reinforces router heuristics so the expanded set holds **64/64 · 42/42**.

AVOIDED worktrees: tip-cv, tip-distance-*, tip-hardneg-r12..r19, tip-pillars*, tip-inverse*, tip-circ*, tip-future*, tip-tti*, tip-choose*.

Pillars side `@ b536f57` (26→34) is separate — do not collide; fold later elsewhere.

## Coverage before → after

| | before (tip / gap) | after (this side) |
|--|--------------------|-------------------|
| LP router | tip **43/43**; expanded gap **52/64** | **64/64** |
| LP verifier | tip **32/32**; expanded **42/42** | **42/42** |
| Mixed (d) unified | **1.0** | **1.0** held |
| `ent_never_on_python` | true | true |
| R2–R12 floors | held | **held** (R5 44/44·36/36 · R7 52/52·44/44 · R12 52/52·44/44) |
| Pillars (tip) | 26/26 | 26/26 (no collide) |

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

## Anti-contam

| Check | Result |
|-------|--------|
| `prompt_touches_gt` | **false** |
| writes to `data/lora_adapter/` | **false** |
| `ro_mtime_unchanged` | **true** |
| tip vis pillar | **BASE** |
| merge main | **no** |
| fold into tip | **no** |

## Freeze?

**YES.** Clear rise **52/64→64/64** **and** solid expand **43→64** (100% ≥80%) **and** verifier **42/42** **and** mixed 1.0 **and** R2–R12 held.

## Reproduce

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-label-protect-expand
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
unset PYTHONPATH
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_label_protect_mixed_router.json
.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_label_protect_python_items.json \
  --hardneg-router data/bench_live/hardneg_label_protect_mixed_router.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## What this does NOT do

- Fold into `frontier/codigo-vivo-tip`
- Touch `data/lora_adapter/`
- Merge main
- Collide with pillars-reinforce side (`b536f57`)
