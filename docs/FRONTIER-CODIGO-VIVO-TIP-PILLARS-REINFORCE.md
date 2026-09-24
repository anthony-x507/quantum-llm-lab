# FRONTIER — Código-vivo tip pillars-reinforce (side)

**Status:** **SIDE ONLY — NOT FOLDED** into `frontier/codigo-vivo-tip`  
**Branch:** `frontier/tip-pillars-reinforce`  
**Base tip:** `f052420` (post distance-far fold pin; origin tip)  
**When:** 2026-09-24 ~14:40–15:05 ET · Mac-111 (`074c6626-…`)  
**Claim:** NO quantum advantage. Expand + reinforce mixed pillar routing coverage; tip vis stays BASE.

## SHA / setup

| Field | Value |
|-------|-------|
| Tip base SHA | `f052420` |
| Branch | `frontier/tip-pillars-reinforce` |
| Host | Mac-111 |
| Model | `mlx-community/Qwen3-VL-8B-Thinking-4bit` |
| Adapters | **READ-ONLY** (`ro_mtime_unchanged=true`) |
| Fold into tip | **false** |

## Why

Tip pillars sat at **26/26**. Coverage gaps tip currently misses (Spanish `programa:` / `código ejecutable` / `imprime`, English `Write code` without `python` token, and `No python code` + `gates=[H, CNOT]` false-positive ops allow-list) were not in the bench. This side branch adds **+8** pillar cases and reinforces router heuristics so the expanded set holds **34/34**.

AVOIDED worktrees: tip-cv, tip-distance-*, tip-hardneg-r12..r18, tip-inverse-r3, tip-circ-expand, tip-future-track*, tip-tti*, tip-choose-safest-n.

## Coverage before → after

| | before (tip) | gap (expand, unfixed) | after (this side) |
|--|--------------|-----------------------|-------------------|
| Pillars routing | **26/26** | **30/34** | **34/34** |
| Hardneg smoke | **18/18** | **18/18** | **18/18** |
| Mixed (d) unified | **1.0** | — | **1.0** held |
| `ent_never_on_python` | true | true | true |
| R2–R12+LP floors | held | — | **held** (R5 44/44 · R7 52/52 · LP 43/43 · R12 52/52) |

## New pillar cases (+8)

| id | pillar | expected | tip miss mode |
|----|--------|----------|---------------|
| `py_es_prog_01` | python | python | Spanish Programa:/imprime (no python token) |
| `py_es_cod_01` | python | python | Spanish Código ejecutable |
| `py_write_code_01` | python | python | Write code (no python token) |
| `py_exec_snip_01` | python | python | Executable snippet + prints |
| `ent_en_bell_01` | entanglement | ent | English Bell JSON ask |
| `ent_nop_y_01` | entanglement | ent | No python code + gates=[H, CNOT] |
| `vis_es_obs_01` | vision | vision | Spanish Observa la imagen (routing-only) |
| `vis_board_01` | vision | vision | chalkboard cue (routing-only) |

## Router reinforce (RO adapters)

1. **PYTHON_RE** — add `write code`, `prints?`, `programa:`, `código ejecutable`, `imprime`/`imprima`.
2. **py disclaimer** — `No python code` / `sin código python` clears `has_py`.
3. **gates_ops_label** — quantum gate lists (`gates=[H, CNOT]`, Hadamard, …) are circuit JSON asks, **not** k8s allow-lists; keep `not gates=[Hadamard]` floor shields (R5/R7).

## Anti-contam

| Check | Result |
|-------|--------|
| `prompt_touches_gt` | **false** |
| writes to `data/lora_adapter/` | **false** |
| `ro_mtime_unchanged` | **true** (2026-09-24 00:58:09) |
| tip vis pillar | **BASE** |
| merge main | **no** |
| fold into tip | **no** |

## Freeze?

Manifest: `data/freeze_manifests/codigo_vivo_tip_pillars_reinforce_100pct_20260924_144425.json`

**YES.** Solid expand **26/26→34/34** **and** clear reinforce of tip misses (gap 30/34→34/34 = 100% ≥80%) **and** mixed floor 1.0 held **and** R2–R12+LP held.

## Reproduce

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-pillars-reinforce
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
unset PYTHONPATH
.venv/bin/python examples/moe_verifier_mixed_live.py --smoke \
  --out data/frontier_moe_verifier_mixed_smoke_pillars_after.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval \
  --out data/frontier_moe_verifier_mixed_cpu_pillars_after.json
# floors
for r in r2 r3 r4 r5 r6 r7 r8 r9 r10 r11 r12 label_protect; do
  .venv/bin/python examples/moe_dual_lane_router.py --hardneg \
    --hardneg-path data/bench_live/hardneg_${r}_mixed_router.json
done
```

## What this does NOT do

- Fold into `frontier/codigo-vivo-tip`
- Touch `data/lora_adapter/`
- Merge main
- Expand circ axis (still tip 2/2 until circ-expand folds elsewhere)
