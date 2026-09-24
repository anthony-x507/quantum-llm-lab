# Frontier — tip motion-r3 (coverage reinforce UPWARD)

**Status:** SIDE BRANCH `frontier/tip-motion-r3` (NOT folded; tip-cv / tip-collision-n / tip-hardneg-r9 / tip-motion-r2 / tip-distance-danger / tip-collision-pred AVOIDED)  
**Base tip:** `3d05cbe` (`frontier/codigo-vivo-tip` with collision-n folded; motion-r2 already on tip)  
**When:** measure 2026-09-24 13:33:33 ET · Mac-111 (`074c6626-…`)  
**Freeze:** `codigo_vivo_tip_motion_r3_100pct_20260924_133333` (≥80% coverage; sha 1d2ca87)  
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

- No merge to `main` / no tip FF (side branch only).
- No `lora_adapter` writes.
- No CloudAgent. Does **not** touch tip-cv / tip-collision-n / tip-hardneg-r9 / tip-motion-r2 / tip-distance-danger / tip-collision-pred WTs.
- No quantum-advantage marketing.
