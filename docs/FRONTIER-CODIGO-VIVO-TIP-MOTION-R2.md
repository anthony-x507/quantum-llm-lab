# Frontier — tip motion-r2 (coverage reinforce UPWARD)

**Status:** **FOLDED** into `frontier/codigo-vivo-tip` (see FOLDED section)  
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

- No merge to `main`.
- No `lora_adapter` writes.
- No CloudAgent.
- No quantum-advantage marketing.
- Tip FF completed — see FOLDED.


## FOLDED into tip

**When:** 2026-09-24 13:23:34 ET · Mac-111 (`074c6626-…`)  
**Method:** rebase `frontier/tip-motion-r2` (`9649df2` / feat `c3cd0a4`) onto tip `4fe070e` → `77d161a` + pin `4d91a9c`; FF into tip (mixed JSON conflicts kept tip; re-smoke).  
**Prior freezes retained (not abandoned):** platform, mlx_r3, post_polish, R5, label_protect, R6, post_od2, R7, **scaffold_motion** `codigo_vivo_tip_scaffold_motion_100pct_20260924_130131`, **R8** `codigo_vivo_tip_r8_100pct_20260924_130950`, **distance_danger** `codigo_vivo_tip_distance_danger_100pct_20260924_131243`, **collision_pred** `codigo_vivo_tip_collision_pred_100pct_20260924_131846`.  
**Re-smoke:** mixed (d) **1.0**; R8 **52/52·44/44**; LP **43/43·32/32**; pillars **26/26**; smoke **12/12**; motion coverage **91%** (132 ind + 50 corr / n=200; +47.0 pp vs 44%); `scene_0222=independent`; `wired_to_vlm=true`; `gt_leak=false`; `ent_never_on_python=true`.  
**Collision held:** physics oracle **100%** (555/555 · 8 eval; prior EVAL artifact; motion fold did not touch collision paths).  
**Adapters:** `data/lora_adapter/` RO mtime unchanged (2026-09-24 10:57:17).  
**Freeze:** `codigo_vivo_tip_motion_r2_100pct_20260924_131537` (side freeze pinned on tip after fold).
