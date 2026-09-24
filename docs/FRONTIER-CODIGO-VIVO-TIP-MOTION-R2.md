# Frontier — tip motion-r2 (coverage reinforce UPWARD)

**Status:** SIDE BRANCH `frontier/tip-motion-r2` (NOT folded; tip-cv / R8 / hardneg-r8 / distance-danger / collision-pred AVOIDED)  
**Base tip:** `d892398` (`frontier/codigo-vivo-tip` with scaffold-motion folded)  
**When:** measure 2026-09-24 13:15:37 ET · Mac-111 (`074c6626-…`)  
**Freeze:** `codigo_vivo_tip_motion_r2_100pct_20260924_131537` (≥80% coverage)  
**Claim:** NO quantum advantage. GT-free RGB centroid motion cue reinforce only.

## LOCK

- Mixed (d) unified **≥0.9667** prefer **1.0** — held **1.0** (re-smoke --cpu-eval).
- Scaffold-motion freeze **retained 100%** — polish UPWARD only; honesty rules unchanged.
- `wired_to_vlm` / `ent_never_on_python` / `prompt_touches_gt=false` unchanged.
- `data/lora_adapter/` READ-ONLY. No merge to `main`. No CloudAgent.
- Escalate **only** on `color_track_fail` — never overrides a known hard-hue cue.

## What changed (reinforce)

1. **Stage 1** — frozen hard {red,blue,green,yellow} path identical to scaffold-motion.
2. **Stage 2** — on track-fail: cyan/magenta/orange/white + soft_* / purple / brown; occlusion-tolerant (min_pts=2).
3. **Stage 3** — single-hue spatial split + chromatic connected components (same-tint / occlusion / approach geometry).
4. **Honesty rules frozen** — `dist_cv≥0.10`⇒independent; locked dist + high `|vel_corr|`⇒correlated; else unknown. No invented distance.
5. **Cheap** `data/scenes/scene_0155` → QLAB_DATA symlink (live MLX path fix).

## Metric deltas

| Surface | Before (scaffold-motion freeze) | After (motion-r2) |
|---------|----------------------------------|-------------------|
| Motion known coverage (n=200) | **44%** (73 ind + 15 corr) | **91%** (132 ind + 50 corr) |
| Delta | — | **+47.0 pp** |
| Remaining unknown | 112 (101 track_fail + 11 ambiguous) | 18 (2 track_fail + 16 ambiguous) |
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
| hard-known cues overridden by soft path | **0** |

## Gap (honest)

- 2 scenes remain `color_track_fail` (single-tint mass that will not split cleanly under chroma/sep gates): `scene_0075`, `scene_0140`.
- 16 remain `corr_ambiguous` under frozen honesty bands (do not invent).

## Reproduce

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-motion-r2
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python -c "..."  # see data/frontier_tip_motion_r2_cue_probe.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `examples/circuit_graph_moe_scaffold.py` — cascade reinforce inside `visual_motion_cue`
- `data/frontier_tip_motion_r2_cue_probe.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-MOTION-R2.md` (this file)
- `data/freeze_manifests/codigo_vivo_tip_motion_r2_100pct_20260924_131537.json`

## What this does NOT do

- No merge to `main` / no tip FF (side branch only).
- No `lora_adapter` writes.
- No CloudAgent. Does **not** touch tip-cv / R8 / hardneg-r8 / distance-danger / collision-pred / tip-scaffold-motion WTs.
- No quantum-advantage marketing.
