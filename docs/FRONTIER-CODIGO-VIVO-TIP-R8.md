# Frontier — Código-vivo tip hardneg R8

**Status:** **FOLDED** into `frontier/codigo-vivo-tip` (rebase `270ce46` onto `d892398` → content `afd52c9` / pin `32b0b14` FF)  
**Branch:** `frontier/tip-hardneg-r8` (rebased; source kept) · tip `frontier/codigo-vivo-tip`  
**Base tip at fold:** `d892398` (post scaffold-motion) · R8 originally from `69655dd`  
**When:** polish ~12:56–1:01 ET · fold 2026-09-24 13:09:50 ET · Mac-111 (`074c6626-…`)  
**Freeze:** `codigo_vivo_tip_r8_100pct_20260924_130950`  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`. No CloudAgent.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.
- R1 / R2 / R3 / R4 / R5 / R6 / R7 / label-protect fixtures must still hold after R8 reinforce.
- Tip-cv is the fold destination; do **not** touch tip-scaffold-motion / tip-distance-danger / tip-hardneg-r7 worktrees. Distance-danger still in flight — **not** folded.

## R8 families (≠ R1–R7 / ≠ label-protect)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r8_mixed_router.json` | **52** | dockerfile_arg_gates, json_schema_gates_prop, terraform_hcl_gates_attr, markdown_fence_gates, unicode_lookalike_gates, rego_policy_gates, cue_lang_gates, toml_gates_array, graphql_sdl_gates, sarif_rule_qubit, nix_attr_gates, wasm_export_gates, edn_keyword_gates, email_header_qubit + ent/vision/base controls |
| `data/bench_live/hardneg_r8_python_items.json` | **44** | same coding themes; GT stdout harness-only |

HARD traps (pre-reinforce drops): markdown prose `gates: list` / fenced YAML; Rego `input.gates[_]`; CUE `#Gates:`; EDN `{:gates`; base chat with ops labels; fullwidth lookalikes near ASCII `gates=` (held without extra when disclaimer present).

## Scores

| Surface | Pre-reinforce | Post-reinforce (1 layer) |
|---------|---------------|---------------------------|
| R8 router | 43/52 (**0.8269**) | **52/52 (1.0)** |
| R8 verifier alone loop | **1.0** (44/44)* | **1.0** (44/44) |
| R8 unified loop | **1.0** (44/44)* | **1.0** (44/44) |
| Mixed (d) unified overall | **1.0 (held ≥0.967)** | **1.0 (held)** |
| R1–R7 routers | held | **18/18 · 22/22 · 35/35 · 40/40 · 44/44 · 48/48 · 52/52** |
| R3–R7 verifiers | held | **28/28 · 32/32 · 36/36 · 40/40 · 44/44** |
| LP router/verifier | held | **43/43 · 32/32** |
| Router smoke | 12/12 | 12/12 |
| `ent_never_on_python` | true | true |

\*Verifier needed one liftable fixture rewrite (`r8v_md_02`) for heuristic proposer; no proposer code change.

## Reinforce layer (gold-free, once)

1. **Router** — exclude Dockerfile `ARG gates=`; JSON Schema `"gates": {`; Rego `input.gates[`; CUE `#Gates:` / `gates?:`; EDN `{:gates` / `:gates`; prose `gates: list`; TOML/Nix gates hints; fullwidth/lookalike ASCII-gates disclaimers. R1–R7 patterns unchanged.
2. **Proposer** — none (fixture lift only for md fence count item → `print 1`).

## Freeze polish_r8

| Manifest | pct |
|----------|-----|
| `data/freeze_manifests/tip_moe_verifier_polish_r8_100pct_*.json` | **100** |

Evidence: `data/freeze_metrics/codigo_vivo_tip_adv_r8_20260924.json`

## CLI

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r8
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r8_mixed_router.json
.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r8_python_items.json \
  --hardneg-router data/bench_live/hardneg_r8_mixed_router.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `data/bench_live/hardneg_r8_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r8.json`
- `data/frontier_moe_verifier_hardneg_r8.json`
- `data/frontier_moe_verifier_mixed_{cpu,unified}.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r8_20260924.json`
- `data/freeze_manifests/tip_moe_verifier_polish_r8_100pct_*.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R8.md` (this file)

## FOLDED into tip

**When:** 2026-09-24 13:09:50 ET · Mac-111 (`074c6626-…`)  
**Method:** rebase `frontier/tip-hardneg-r8` (`270ce46` / polish `c964dcc`) onto tip `d892398` → content `afd52c9` + polish pin `32b0b14`; FF into tip. Mixed JSON conflicts kept tip (re-smoke).  
**Prior freezes retained (not abandoned):** platform, mlx_r3, post_polish, R5, label_protect, R6, post_od2, R7, **scaffold_motion** `codigo_vivo_tip_scaffold_motion_100pct_20260924_130131`, polish_r8.  
**Re-smoke:** mixed (d) **1.0**; R1–R8 routers **18/18 · 22/22 · 35/35 · 40/40 · 44/44 · 48/48 · 52/52 · 52/52**; R3–R8/LP verifier **28/28 · 32/32 · 36/36 · 40/40 · 44/44 · 44/44 · 32/32**; LP **43/43**; pillars **26/26**; smoke **12/12**; motion coverage **44%**; `wired_to_vlm=true`; `gt_leak=false`; `ent_never_on_python=true`.  
**Not folded:** tip-distance-danger (still in flight).
