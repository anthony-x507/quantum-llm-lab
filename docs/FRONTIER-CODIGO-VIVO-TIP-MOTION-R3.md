# Frontier — tip motion-r3 (coverage reinforce UPWARD)

**Status:** **FOLDED** into `frontier/codigo-vivo-tip` (see FOLDED section)  
**Base tip:** `3d05cbe` (`frontier/codigo-vivo-tip` with collision-n folded; motion-r2 already on tip)  
**When:** measure 2026-09-24 13:33:33 ET · Mac-111 (`074c6626-…`)  
**Freeze:** `codigo_vivo_tip_motion_r3_100pct_20260924_133333` (≥80% coverage; post-rebase feat `fbe296a`)  
**Claim:** NO quantum advantage. GT-free RGB centroid motion cue reinforce only.

## LOCK

- Mixed (d) unified **≥0.9667** prefer **1.0** — held **1.0** (re-smoke --cpu-eval).
- Motion-r2 / scaffold-motion freezes **retained** — polish UPWARD only; honesty rules unchanged.
- `wired_to_vlm` / `ent_never_on_python` / `prompt_touches_gt=false` unchanged.
- `data/lora_adapter/` READ-ONLY. No merge to `main`. No CloudAgent.
- Escalate **only** on `corr_ambiguous` (Stage 4) — never overrides a known Stage 1–3 cue.

## What changed (reinforce)

1. **Stages 1–3** — frozen identical to motion-r2 (hard hues → extended/soft → single-hue split / chroma comps).
2. **Stage 4a — tracking continuity densify** — on `corr_ambiguous` only: re-track the same hue pair on denser frames (`every=1`, up to 16) with bidirectional gap fill; re-apply **frozen** honesty bands.
3. **Stage 4b — approach/recede** — if still unknown after densify: relative distance range `drel=(dmax−dmin)/(dmean+ε) ≥ 0.18` ⇒ **independent** (distance not locked; product-like). Does not invent locked-distance correlated labels.
4. **Honesty rules frozen** — `dist_cv≥0.10`⇒independent; locked dist + high `|vel_corr|`⇒correlated; else unknown. No invented distance.

## Metric deltas

| Surface | Before (motion-r2 freeze) | After (motion-r3) |
|---------|---------------------------|-------------------|
| Motion known coverage (n=200) | **91%** (132 ind + 50 corr) | **97.5%** (138 ind + 57 corr) |
| Delta vs r2 | — | **+6.5 pp** |
| Remaining unknown | 18 (2 track_fail + 16 ambiguous) | 5 (2 track_fail + 3 ambiguous) |
| `scene_0222` | independent | **independent** (held, stage=hue_hard) |
| Mixed (d) unified | 1.0 | **1.0** (floor held) |
| gt_free / reads_meta / inference_uses_gt | true/false/false | **held** |

## Anti-contam

| Check | Result |
|-------|--------|
| `gt_free` on all probed cues | **true** |
| `reads_meta` | **false** |
| `inference_uses_gt` | **false** |
| unknown suffix honesty | present |
| hard-known Stage 1–3 cues overridden by Stage 4 | **0** |

## Gap (honest)

- 2 scenes remain `color_track_fail` (single moving green blob; no second GT-free track): `scene_0075`, `scene_0140`.
- 3 remain `corr_ambiguous` under frozen honesty bands after continuity densify: `scene_0002`, `scene_0010`, `scene_0152` (mid `|vel_corr|`, locked/near-locked distance — do not invent).

## Reproduce

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-motion-r3
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python -c "..."  # see data/frontier_tip_motion_r3_cue_probe.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `examples/circuit_graph_moe_scaffold.py` — Stage 4 continuity + approach/recede inside `visual_motion_cue`
- `data/frontier_tip_motion_r3_cue_probe.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-MOTION-R3.md` (this file)
- `data/freeze_manifests/codigo_vivo_tip_motion_r3_100pct_20260924_133333.json`

## What this does NOT do

- No merge to `main`.
- No `lora_adapter` writes.
- No CloudAgent. Does **not** touch tip-hardneg-r10 / tip-vision-delta / tip-hardneg-r9 / tip-collision-n / tip-motion-r2 WTs.
- No quantum-advantage marketing.
- Tip FF completed — see FOLDED.


## FOLDED into tip

**When:** 2026-09-24 13:38:30 ET · Mac-111 (`074c6626-…`)  
**Method:** rebase `frontier/tip-motion-r3` (`24798e3` / feat `1d2ca87`) onto tip `2d13d0a` → `fbe296a` + pin `553b7e5`; FF into tip (mixed JSON conflicts kept tip; re-smoke).  
**Prior freezes retained (not abandoned):** platform, mlx_r3, post_polish, R5, label_protect, R6, post_od2, R7, **scaffold_motion**, **R8**, **distance_danger**, **collision_pred**, **motion_r2**, **collision_n**, **R9** `codigo_vivo_tip_r9_100pct_20260924_133405`.  
**Re-smoke:** mixed (d) **1.0**; R9 **52/52·44/44**; motion coverage **97.5%** (138 ind + 57 corr / n=200; +6.5 pp vs 91%); `scene_0222=independent`; pillars **26/26**; smoke **12/12**; collision physics **100%** (n=40 / 2850; prior freeze; motion fold did not touch collision paths); `wired_to_vlm=true`; `gt_leak=false`; `ent_never_on_python=true`.  
**Not folded:** tip-hardneg-r10 / tip-vision-delta (active — do not fold).  
**Adapters:** `data/lora_adapter/` RO mtime unchanged (2026-09-24 10:57:17).  
**Freeze:** `codigo_vivo_tip_motion_r3_100pct_20260924_133333` (side freeze pinned on tip after fold).
