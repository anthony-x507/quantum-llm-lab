# FRONTIER — Código-vivo tip vision-ground

**Status:** **FOLDED** into `frontier/codigo-vivo-tip` (rebase `5a74c4a`/`06017ae`/`04b0738`/`810a8bf` onto `9cc5ed5` → content `78ce050` / pins `5775665`+`2c5f1e5`+`ec65f66` FF)  
**Branch:** `frontier/tip-vision-ground` (rebased; source kept) · tip `frontier/codigo-vivo-tip`  
**Base tip at fold:** `9cc5ed5` (post inverse-r2) · vision originally from `6624df1`  
**When:** polish ~13:44 ET · fold 2026-09-24 13:55:13 ET · Mac-111 (`074c6626-…`)  
**Freeze:** `codigo_vivo_tip_vision_ground_100pct_20260924_134441`  
**Claim:** NO quantum advantage. BASE vision prompt/parse/grounding only; tip vis stays BASE.

## SHA / setup

| Field | Value |
|-------|-------|
| Tip base SHA | `6624df1` (`6624df1e9bdad1cdb7ddb4cb925ae018bb93968c`) |
| Branch | `frontier/tip-vision-ground` |
| Branch SHA | `06017ae` (`06017ae2e59f3d11cc4589ba139df329b2433fe6`) · feat `5a74c4a` |
| Host | Mac-111 (`074c6626-…`) |
| Adapters | **READ-ONLY** (`ro_mtime_unchanged=true` on `*.safetensors`) |
| Freeze | `codigo_vivo_tip_vision_ground_100pct_20260924_134441` |

### Adapter RO mtimes (ET)

| Adapter | adapters.safetensors mtime | Role on tip |
|---------|---------------------------|-------------|
| `data/lora_adapter/` | 2026-09-24 **00:58** | quantum RO; **not** on tip vision |
| `data/lora_adapter_ent2/` | 2026-09-24 **09:02** | MoE **ent** lane |
| `data/lora_adapter_classical/` | 2026-09-24 **05:29** | present; **not** routed on CV pillars |

## Why this branch (after tip-vision-delta)

Prior `frontier/tip-vision-delta` @ `b83ec50` showed quantum RO adapter hurts vision (**−0.200** raw / **−0.100** parse ceiling). Tip policy: **keep vis on BASE**. Irreducible gaps closed here without writing any LoRA dir:

1. Circuit grounding: explicit **X** before CX/CNOT on bench vision circuit items
2. Anti-think JSON-only cue (+ phase-2 retry) on vision circuit items
3. Parse: bare `pi/2` sanitize; gold-free **narrative→gates** fallback when Thinking narrates but never emits `{...}`
4. Hold dual-lane floor unified **1.0**; tip vis pillar stays BASE

AVOIDED worktrees: tip-cv, tip-hardneg-r10, tip-vision-delta, tip-motion-r3, tip-hardneg-r9.

## Anti-contam

| Check | Result |
|-------|--------|
| `prompt_touches_gt` | **false** (cues never embed `expected_gates`) |
| CLEAN? | **YES** |
| `ent_never_on_python` | **true** |
| writes to `data/lora_adapter/` | **false** |
| `ro_mtime_unchanged` (safetensors) | **true** |
| new LoRA dir | **none** |

## BASE vision before → after (same fixtures)

Source before: locked `BENCHMARK_CODIGO_VIVO.json` base.vision · After: this branch `--base-only --skip-python --skip-ent`.

| | before | after | Δ |
|--|--------|-------|---|
| Vision accuracy | **0.900** (9/10) | **1.000** (10/10) | **+0.100** |
| `vis_circ_01` | true (H,X,CNOT) | **true** (held; grounded) | held |
| `vis_circ_02` | **false** (parse:JSONDecodeError / narrative burn) | **true** (RY,Z via grounded+narrative parse) | **rescued** |
| Circ axis | 1/2 = 50% | **2/2 = 100%** | +50 pp |

### What rescued `vis_circ_02`

BASE Thinking-4bit correctly *described* `RY(pi/2)` then `Z` but burned tokens on English prose and never emitted JSON (`max_tokens=512` era). This branch:

- Appends GT-free **CIRCUIT GROUNDING** + **ANTI-THINK JSON-ONLY** suffix (`vision/grounding.py`)
- Raises circuit `max_tokens` to 1024 + JSON-only retry
- Sanitizes bare `pi/2` in `parsear_propuesta`
- **Narrative fallback** extracts ordered gates from prose when JSON missing (gold-free; no expected_gates consult)

`vis_circ_01` held; cue also reinforces explicit **X** before CX (the failure mode seen under quantum RO on tip-vision-delta).

## Tip mixed floor (held)

CPU `--cpu-eval` @ this branch:

| Path | python | ent | vision | overall |
|------|--------|-----|--------|---------|
| (a) baseline | 0.000 | 0.000 | 1.000 | 0.333 |
| (b) MoE alone | 0.000 | **1.000** | 1.000 | 0.667 |
| (c) verifier-on-python | **1.000** | 0.000 | 1.000 | 0.667 |
| (d) unified | **1.000** | **1.000** | **1.000** | **1.000** |

pillars **26/26** · hardneg smoke **18/18** · `ent_never_on_python` · freezes retained (r9 / collision_n / motion_r2 / distance / collision_pred / label-protect / scaffold + priors). Tip vis routing stays **BASE**.

## Freeze?

**YES.** Criterion: measurable rise **AND** floor held **AND** ≥80% on reinforced axis.

| Gate | Result |
|------|--------|
| Rise | 0.9 → **1.0** (+0.1) |
| Floor unified | **1.0** held (≥0.9667) |
| Reinforced axis (circ) | **2/2 = 100%** ≥80% |

Manifest: `data/freeze_manifests/codigo_vivo_tip_vision_ground_100pct_20260924_134441.json`

## Reproduce

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-vision-ground
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
unset PYTHONPATH
# images are gitignored — symlink once:
# ln -sfn "$QLAB_DATA/bench_live/vision_items" data/bench_live/vision_items
.venv/bin/python examples/bench_codigo_vivo.py \
  --skip-python --skip-ent --base-only \
  --out data/frontier_tip_vision_ground_bench_after.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval \
  --out data/frontier_moe_verifier_mixed_cpu_vision_ground.json
.venv/bin/python examples/moe_verifier_mixed_live.py --smoke \
  --out data/frontier_moe_verifier_mixed_smoke_vision_ground.json
```

## Artifacts

- `data/frontier_tip_vision_ground_scoreboard.json` (SSOT)
- `data/frontier_tip_vision_ground_before.json`
- `data/frontier_tip_vision_ground_bench_after.json`
- `data/frontier_moe_verifier_mixed_{cpu,smoke}_vision_ground.json`
- `data/tip_vision_ground_adapter_ro_snapshot_{before,after}.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-VISION-GROUND.md` (this file)
- `data/freeze_manifests/codigo_vivo_tip_vision_ground_100pct_20260924_134441.json`



## FOLDED into tip

**When:** 2026-09-24 13:55:13 ET · Mac-111 (`074c6626-…`)  
**Method:** rebase `frontier/tip-vision-ground` (`810a8bf` / feat `5a74c4a`; pins `06017ae`+`04b0738`+`810a8bf`) onto tip `9cc5ed5` → `78ce050`+`5775665`+`2c5f1e5`+`ec65f66`; FF into tip (STATUS kept inverse-r2 fold + vision side note; relative mixed_unified primary kept).  
**Prior freezes retained (not abandoned):** platform, mlx_r3, post_polish, R5, label_protect, R6, post_od2, R7, **scaffold_motion**, **R8**, **distance_danger**, **collision_pred**, **motion_r2**, **collision_n**, **R9**, **motion_r3**, **R10**, **inverse_r2** `codigo_vivo_tip_inverse_r2_100pct_20260924_134326`.  
**Re-smoke:** mixed (d) **1.0**; vision BASE **1.000** (10/10); circ **2/2**; inverse_cv **99.82%**; collision physics **100%** (n=40 / 2850); choose_safest **100%**; R10 **52/52·44/44**; motion coverage **97.5%** (138 ind + 57 corr); pillars **26/26**; hardneg **18/18**; `wired_to_vlm=true`; `gt_leak=false`; `ent_never_on_python=true`.  
**Not folded:** tip-motion-r4 / tip-hardneg-r11 / tip-distance-mid / tip-tti (active — do not fold).  
**Adapters:** `data/lora_adapter/` RO mtime unchanged (2026-09-24 00:58:09). Tip vis pillar stays **BASE**.  
**Freeze:** `codigo_vivo_tip_vision_ground_100pct_20260924_134441` (pinned on tip after fold).

## What this does NOT do

- No write to `data/lora_adapter/` or any new LoRA directory (Anthony may authorize a vision LoRA later — not this brief).
- No merge to `main`. Fold destination is tip-cv only.
- No tip-motion-r4 / tip-hardneg-r11 / tip-distance-mid / tip-tti worktree writes.
- No quantum-advantage marketing.
