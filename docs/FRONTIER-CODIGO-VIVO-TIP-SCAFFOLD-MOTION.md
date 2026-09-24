# Frontier — tip scaffold→VLM + motion/RGB cue honesty

**Status:** **FOLDED** into `frontier/codigo-vivo-tip` @ `7b0c63b` (2026-09-24 13:01:31 ET)  
**Branch:** `frontier/tip-scaffold-motion` (rebased `9ddfaed` → `7b0c63b` onto tip post-R7 `69655dd`)  
**When:** measure ~12:55 ET · fold 2026-09-24 13:01:31 ET · Mac-111 (`074c6626-…`)  
**Freeze:** `codigo_vivo_tip_scaffold_motion_100pct_20260924_130131`  
**Claim:** NO quantum advantage. GT-free RGB centroid motion cue + text scaffold → VLM only.

## LOCK

- Mixed (d) unified **≥0.9667** prefer **1.0** — held **1.0**.
- `wired_to_vlm=true` (`channel=text_scaffold_prefix`); `weight_peft_injection=false`.
- `ent_never_on_python=true`; `prompt_touches_gt=false`; motion cue **never** reads `meta` labels.
- `data/lora_adapter/` READ-ONLY. No merge to `main`.
- Freezes retained: post_od2 + r7 `codigo_vivo_tip_r7_100pct_20260924_125600` + r6 + LP + priors + **this** scaffold_motion freeze.

## What changed (small reinforce)

1. **Multi-hue RGB tracks** — pick two strongest among {red, blue, green, yellow} (was red/blue only).
2. **Honesty rules** — `dist_cv ≥ 0.10` ⇒ independent (varying separation); locked distance + high `|vel_corr|` ⇒ correlated; else unknown with explicit prompt honesty (do not invent entanglement from color).
3. **Scaffold→VLM meta** — `bench_codigo_vivo` attaches `motion_cue` / `motion_cue_gt_free` into scaffold wire meta.
4. **Probe** — `data/frontier_tip_scaffold_motion_cue_probe.json` (n=200 survey).

## Metric deltas

| Surface | Before (approx, red/blue only) | After |
|---------|--------------------------------|-------|
| Motion known coverage (n≈200) | ~low teens % | **44%** (73 ind + 15 corr) |
| `scene_0222` cue | independent | **independent** (held) |
| `wired_to_vlm` | true | **true** · gt_leak=false |
| Scaffold Δsolve / hard Δsolve | 0.5 / 0.6666 | **0.5 / 0.6666** (held) |
| Mixed (d) unified | 1.0 | **1.0** (floor held) |
| Hardneg R1 / LP | 18/18 · 43/43 | **held** |

Own-delta vision RAW (−0.200 under quantum adapter alone) is **unchanged** — tip still uses BASE for vision; this branch does not apply quantum LoRA to vis.

## Anti-contam

| Check | Result |
|-------|--------|
| `gt_free` on all probed cues | **true** |
| `reads_meta` | **false** |
| `inference_uses_gt` | **false** |
| unknown suffix honesty | present |
| scaffold `gt_leak` (wire smoke) | **false** |

## Reproduce

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-scaffold-motion
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
# optional: ln -sfn "$QLAB_DATA/scenes" data/scenes
.venv/bin/python examples/circuit_graph_moe_scaffold.py --wire-vlm --polish
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `examples/circuit_graph_moe_scaffold.py` — multi-hue + honesty rules + unknown suffix
- `examples/bench_codigo_vivo.py` — motion_cue meta on scaffold→VLM
- `data/frontier_tip_scaffold_motion_cue_probe.json`
- `data/frontier_scaffold_wire_vlm.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-SCAFFOLD-MOTION.md` (this file)

## Fold

- Path: rebase `9ddfaed` onto tip `69655dd` → `7b0c63b`, then FF into `frontier/codigo-vivo-tip`.
- Re-smoke: mixed (d) unified **1.0**; R1–R7 routers+verifiers held; LP **43/43·32/32**; R7 **52/52·44/44**; pillars **26/26**; smoke **12/12**; `wired_to_vlm=true`; `ent_never_on_python=true`; motion coverage **44%** (73 ind + 15 corr / n=200); gt_leak=false.
- Freezes **retained** (never abandoned): platform / mlx_r3 / post_polish / r5 / label_protect / r6 / post_od2 / r7.
- Tip freeze: `codigo_vivo_tip_scaffold_motion_100pct_20260924_130131`.

## What this does NOT do

- No merge to `main`.
- No `lora_adapter` writes (RO mtime held).
- No CloudAgent. Does **not** fold R8 (still running on side).
- No quantum-advantage marketing.
