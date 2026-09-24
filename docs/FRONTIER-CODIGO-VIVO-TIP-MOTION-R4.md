# Frontier — tip motion-r4 (coverage reinforce UPWARD)

**Status:** SIDE BRANCH `frontier/tip-motion-r4` (NOT folded; tip-cv / tip-hardneg-r10 / tip-inverse-r2 / tip-vision-ground / tip-motion-r3 AVOIDED)  
**Base tip:** `6624df1` (`origin/frontier/codigo-vivo-tip` post motion-r3 fold)  
**When:** measure 2026-09-24 13:50:17 ET · Mac-111 (`074c6626-…`)  
**Freeze:** `codigo_vivo_tip_motion_r4_100pct_20260924_135017` (≥80% coverage; sha PENDING)  
**Claim:** NO quantum advantage. GT-free RGB centroid motion cue reinforce only.

## LOCK

- Mixed (d) unified **≥0.9667** prefer **1.0** — held **1.0** (re-smoke --cpu-eval).
- Motion-r3 / motion-r2 / scaffold-motion freezes **retained** — polish UPWARD only; honesty bands unchanged.
- `wired_to_vlm` / `ent_never_on_python` / `prompt_touches_gt=false` unchanged.
- `data/lora_adapter/` READ-ONLY. No merge to `main`. No fold into tip. No CloudAgent.
- Escalate **only** on `corr_ambiguous` (Stage 5a) or `color_track_fail` singleton (Stage 5b) — never overrides a known Stage 1–4 cue.

## What changed (reinforce)

1. **Stages 1–4** — frozen identical to motion-r3 (hard → extended → single-hue/chroma → continuity densify ≤16 + approach/recede).
2. **Stage 5a — axis-wise honesty** — on still-`corr_ambiguous` only: apply the **same** frozen `|vel_corr|` bands (`>0.75` / `<0.45`) **per axis** under locked distance (`dist_cv<0.08`). Mid flat corr with one strong axis ⇒ `axis_locked` correlated; mid flat with both axes weak ⇒ `axis_weak` independent (cross-axis artifact). Optional full-window densify retry uses the same bands.
3. **Stage 5b — singleton mover** — on `color_track_fail` only: exactly one moving chroma blob with no second GT-free partner ⇒ `independent` (`singleton_mover`). Does not invent a pair.
4. **Honesty rules frozen** — `dist_cv≥0.10`⇒independent; locked dist + high `|vel_corr|`⇒correlated; else unknown. Stage 5 does **not** soften thresholds.

## Metric deltas

| Surface | Before (motion-r3 freeze) | After (motion-r4) |
|---------|---------------------------|-------------------|
| Motion known coverage (n=200) | **97.5%** (138 ind + 57 corr) | **100%** (141 ind + 59 corr) |
| Delta vs r3 | — | **+2.5 pp** |
| Remaining unknown | 5 (2 track_fail + 3 ambiguous) | **0** |
| `scene_0222` | independent | **independent** (held, stage=hue_hard) |
| Mixed (d) unified | 1.0 | **1.0** (floor held) |
| gt_free / reads_meta / inference_uses_gt | true/false/false | **held** |

## Rescued (from r3 honest leftovers)

| Scene | Before | After | Mode |
|-------|--------|-------|------|
| `scene_0002` | unknown / corr_ambiguous | **correlated** | axis_locked (cx=0.842) |
| `scene_0010` | unknown / corr_ambiguous | **correlated** | axis_locked (cx=0.921) |
| `scene_0152` | unknown / corr_ambiguous | **independent** | axis_weak (amax=0.341) |
| `scene_0075` | unknown / color_track_fail | **independent** | singleton_mover |
| `scene_0140` | unknown / color_track_fail | **independent** | singleton_mover |

## Anti-contam

| Check | Result |
|-------|--------|
| `gt_free` on all probed cues | **true** |
| `reads_meta` | **false** |
| `inference_uses_gt` | **false** |
| unknown suffix honesty | present |
| hard-known Stage 1–4 cues overridden by Stage 5 | **0** |

## Gap (honest)

- None remaining at n=200 (100% known). Further work would be out-of-sample / larger-n only.

## Reproduce

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-motion-r4
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python -c "..."  # see data/frontier_tip_motion_r4_cue_probe.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `examples/circuit_graph_moe_scaffold.py` — Stage 5 axis honesty + singleton_mover inside `visual_motion_cue`
- `data/frontier_tip_motion_r4_cue_probe.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-MOTION-R4.md` (this file)
- `data/freeze_manifests/codigo_vivo_tip_motion_r4_100pct_20260924_135017.json`

## What this does NOT do

- No merge to `main` / no tip FF (side branch only).
- No `lora_adapter` writes.
- No CloudAgent. Does **not** touch tip-cv / tip-hardneg-r10 / tip-inverse-r2 / tip-vision-ground / tip-motion-r3 WTs.
- No quantum-advantage marketing.
