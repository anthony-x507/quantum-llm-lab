# FRONTIER — tip-choose-safest-n (expand choose_safest coverage + hardneg)

**Branch:** `frontier/tip-choose-safest-n` → **FOLDED** into `frontier/codigo-vivo-tip`  
**Base (side):** tip `9a0de24` (pre R12..R15 stack)  
**Fold base tip SHA:** `422a9e3` (post R15)  
**Fold worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-cv` (Mac-111)  
**When (side):** 2026-09-24 ~14:27 ET · **Fold:** 2026-09-24 15:18:18 ET  
**Side freeze:** `codigo_vivo_tip_choose_safest_n_100pct_20260924_142733`  
**Fold freeze:** `codigo_vivo_tip_choose_safest_n_fold_100pct_20260924_151818`  
**Fold feat SHA:** `PENDING` (filled in pin commit)  
**Feat SHA (side):** `d3bf164` / pin `fecca86`  
**Scope:** Folded into tip-cv. R16+ / tti-cold **not** folded.

## LOCK (Anthony)

- Tip vis pillar stays **BASE**. No LoRA writes.
- Mixed (d) **1.0**, R15 **52/52·44/44**, R14 **52/52**, LP **64/64**, pillars **37/37**, circ **5/5**, track ~**99.34%**, far MAE **2.600**, DZ/mid/TTI **100%** — do not regress.
- choose_safest / physics @ **n=80 / 5670** hold **100%**.
- GT only in eval sidecars; never in prompts / memory / retrieval.
- Quantum `data/lora_adapter/` = **READ-ONLY**.

## What changed

1. **Synth defaults** — `generate.py`: `DEFAULT_N=400`, `DEFAULT_TRAIN=320`, `DEFAULT_EVAL=80`, seed `24092447` (was 200 / 160 / 40 / `24092446`).
2. **Hardneg mix** — `unsafe_look_safe` (~22%), `safe_look_unsafe` (~22%), `near_miss_choice` (~16%), baseline remainder (~40%). Meta tag `hardneg_kind` only (not GT).
3. **Eval corpus** — train 160→320 / eval 40→80; queries 2850→5670.
4. **Probe** — `data/frontier_tip_choose_safest_n_probe.json` (branch retagged tip on fold).
5. **Fold method** — cherry-pick `d3bf164` onto `422a9e3`; conflicts EVAL/probes/harness → side n=80 retagged `frontier/codigo-vivo-tip`; rsync side train/eval frames (gitignored); CPU re-smoke + contam; R15/R14/LP hardneg re-smoke.

## Metrics (CPU physics oracle, GT-only post-hoc) — fold re-smoke

| | before (tip @ collision-n / R15) | after (fold) |
|--|----------------------------------|--------------|
| n_eval_seqs | **40** | **80** |
| n_queries | **2850** | **5670** |
| **collision_physics** | **100.0%** | **100.0%** |
| **collision_choose_safest** | **100.0%** | **100.0%** |
| inverse_cv (tip inverse-r3 @ n80) | 100% @ n40 | **99.89%** |
| contam self-test | PASS | PASS |
| retrieval train∩eval | ∅ | ∅ |

Horizon breakdown (fold):

| predictor | k=1 | k=3 | k=5 | overall |
|-----------|-----|-----|-----|---------|
| **collision_physics** | **100.0** | **100.0** | **100.0** | **100.0** |
| inverse_cv | 99.95 | 99.89 | 99.84 | 99.89 |
| **collision_choose_safest** | **100.0** | **100.0** | **100.0** | **100.0** |

Source: `data/collision_predictive/EVAL_COLLISION_CPU.json`  
Probe: `data/frontier_tip_choose_safest_n_probe.json`

### Floors held on fold

| Surface | Score |
|---------|-------|
| mixed (d) unified | **1.0** (cited / non-touch router) |
| R15 router | **52/52** (re-smoke) |
| R14 router | **52/52** (re-smoke) |
| LP router | **64/64** (re-smoke) |
| pillars / circ | **37/37 · 5/5** (cited non-touch) |
| far MAE / track / DZ/mid/TTI | **2.600 / ~99.34% / 100%** cited |

## Adapters RO

- `data/lora_adapter/` — **no writes** (`.gitkeep` only). Snapshots `data/tip_choose_safest_n_fold_adapter_ro_snapshot_{before,after}.json` — mtime unchanged.
- `data/lora_adapter_collision/` empty (VLM deferred).

## Not folded

R16 @ f3ccb0b → tti-cold @ c97e89a → R17…R25.
