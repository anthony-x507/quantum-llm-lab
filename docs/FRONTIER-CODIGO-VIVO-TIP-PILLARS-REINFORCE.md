# FRONTIER — tip-pillars-reinforce (routing coverage)

**Branch:** `frontier/tip-pillars-reinforce` → **FOLDED** into `frontier/codigo-vivo-tip`  
**Base (side):** tip `f052420` (post distance-far)  
**Fold worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-cv` (Mac-111)  
**When (side):** 2026-09-24 ~14:40–14:45 ET · **Fold:** 2026-09-24 ~14:59 ET  
**Side freeze:** `codigo_vivo_tip_pillars_reinforce_100pct_20260924_144425`  
**Fold freeze:** `codigo_vivo_tip_pillars_reinforce_fold_100pct_20260924_145946`  
**Fold feat SHA:** `PENDING` (pinned in docs commit)  
**Feat SHA (side):** `9cd55eb` (`9cd55ebdbe7e7d6e9199eedd6ef0ddc262f7c5c4`)  
**Scope:** Folded into tip-cv. LP-expand / R14+ **not** folded.

## LOCK (Anthony)

- Tip vis pillar stays **BASE**. No LoRA writes.
- Mixed (d) **1.0**, circ **5/5**, R13 **52/52**, future track **~99.34%**, far MAE **2.600**, DZ/mid/TTI **100%**, inv/collision **100%** — do not regress.
- GT only in eval sidecars; never in prompts / memory / retrieval.
- Quantum `data/lora_adapter/` = **READ-ONLY**.

## What changed

Expand + reinforce mixed pillar routing coverage with **+8** cases tip previously missed:

1. **Python (+4):** ES `Programa:`/`imprime`; ES `Código ejecutable`; EN `Write code`; `Executable snippet` + `prints`.
2. **Entanglement (+2):** EN Bell JSON ask; `No python code` + `gates=[H, CNOT]` (must stay ent).
3. **Vision routing (+2):** ES `Observa la imagen`; chalkboard cue (routing-only, `score_accuracy=false`).
4. **Router reinforce** (`examples/moe_dual_lane_router.py`):
   - `PYTHON_RE` — `write code`, `prints?`, `programa:`, `código ejecutable`, `imprime`/`imprima`.
   - `No python code` / `sin código python` clears `has_py`.
   - Quantum `gates=[H, CNOT]` / Hadamard lists are circuit asks, **not** k8s ops allow-lists; keep `not gates=[Hadamard]` floor shields.

## Metrics (fold re-smoke on tip @ 370f35a)

| | tip before (post circ) | tip after fold |
|--|------------------------|----------------|
| Pillars routing | **29/29** | **37/37** |
| Side trail | 26/26→34/34 | (+8 on tip; circ extras retained) |
| Hardneg smoke | **18/18** | **18/18** |
| Mixed (d) unified | **1.0** | **1.0** held |
| Circ axis | **5/5** | **5/5** retained |
| Vision BASE | **1.000** (13/13) | **1.000** retained (untouched) |

Floors retained: R13 **52/52**; R12 **52/52**; LP **43/43**; R5 **44/44**; R7 **52/52**; future track **99.34%**; far MAE **2.600 m**; DZ/mid/TTI **100%**; inv/collision **100%**; tip vis **BASE**.

Anti-contam: **CLEAN** (`prompt_touches_gt=false`, adapters RO mtime unchanged).  
Caveat: routing coverage expand — **not** a VLM-finetune / quantum-advantage claim.

## Adapters RO

- `data/lora_adapter/` — **no writes** (before/after snapshot equal).
- Tip vis stays BASE (`--base-only`).

## Commands

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-cv
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
unset PYTHONPATH
.venv/bin/python examples/moe_verifier_mixed_live.py --smoke \
  --out data/frontier_moe_verifier_mixed_smoke_pillars_reinforce_fold.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval \
  --out data/frontier_moe_verifier_mixed_cpu_pillars_reinforce_fold.json
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r13_mixed_router.json
```

## Non-goals

- No merge to main.
- No CloudAgent.
- No write to `data/lora_adapter/`.
- LP-expand @ f2b5031 / R14+ remain next-queue only.

## Fold into tip-cv (2026-09-24 ~14:59 ET)

Merge-port side `9cd55eb`/`b536f57` onto tip `370f35a` (post circ-expand): surgical router reinforce + +8 mixed pillar cases; keep circ `vis_circ_03..05` routing extras (29→37). Re-smoke pillars **37/37** · hardneg **18/18**; mixed (d) **1.0**; R13 **52/52**; circ **5/5** retained.

Freeze `codigo_vivo_tip_pillars_reinforce_fold_100pct_20260924_145946`. Floors held. Adapters RO. Tip vis BASE.
