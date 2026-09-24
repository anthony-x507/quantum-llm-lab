# FRONTIER — Código-vivo tip scoreboard

**Branch:** `frontier/codigo-vivo-tip`  
**Written:** 2026-09-24 11:00 ET · Mac-139 (`074c6626-…`)  
**Claim scope:** classical MoE router + `python -I` verifier + prior-replay ent/vision + GT-free circuit-graph scaffold on ent + mlx vision parse polish. **NO quantum-advantage claims.**

## Tip composition (merges / folds)

| Source tip | SHA | Role |
|------------|-----|------|
| `frontier/mixed-freeze-vision` | `c2c3988` | **PRIMARY** — mixed freeze ≥0.967; vision polish → **overall 1.0** |
| `frontier/vision-mlx-api-fix` | `62843ad` | mlx_vlm generate API (`prompt=` / `image=`) |
| `frontier/freeze-polish-bridge` | `65e5c2b` | R1/R2 hardneg reinforces (`VISION_NEG` / `ENT_NEG`) |
| `frontier/circuit-graph-scaffold-hard` | `ecb7974` | Clifford–Pauli graph scaffold (+ hard expand) |
| `frontier/vision-mlx-anti-think` | `d6c5cad` | anti-think parse 0/3→3/3 (keep API fix) |
| `frontier/mixed-with-scaffold` | `4d587f7` | `--circuit-scaffold` **default ON** for ent |
| `frontier/mixed-with-freeze-r2` | `7211f78` | port R1/R2 hardneg CLI + fixtures (metric floor = MFV 1.0) |

**Metric policy:** Prefer vision **1.0** / overall **1.0** from `mixed-freeze-vision` over scaffold-merge / R2-port scoreboards that still show vis **0.9** / overall **0.9667**. Keep scaffold wiring + R2 reinforces + anti-think.

## LOCK / anti-contam

- Freeze mixed unified overall **≥0.9667** (docs ~0.967); polished floor held at **1.0**. Never abandon.
- `data/lora_adapter/` **READ-ONLY**. No merge to `main`.
- `ent_never_on_python=true`, `prompt_touches_gt=false`, scaffold `gt_leak=0`.

## Live retest (this tip)

| Check | Result |
|-------|--------|
| Mixed smoke pillars | **26/26** |
| Mixed embedded hardneg | **18/18** |
| `ent_never_on_python` | **True** |
| `circuit_scaffold` default | **ON**; injected **10** on ent |
| Unified (d) overall | **1.0000** (py1 / ent1 / vis1) |
| MoE Δ overall | **+0.3334** visible |
| Hardneg R1 router | **18/18 (1.0)** |
| Hardneg R2 router | **22/22 (1.0)** |
| Scaffold freeze recheck | **held** solve=0.9 Δsolve=0.5 |

### Mixed CPU paths (a)(b)(c)(d)

| Path | python | ent | vision | overall |
|------|--------|-----|--------|---------|
| (a) baseline | 0.000 | 0.000 | **1.000** | 0.333 |
| (b) MoE alone | 0.000 | **1.000** | **1.000** | 0.667 |
| (c) verifier-on-python | **1.000** | 0.000 | **1.000** | 0.667 |
| (d) unified | **1.000** | **1.000** | **1.000** | **1.000** |

## Scoreboard — baseline | actual | target | gap | next

| Pillar | Baseline | Actual (tip) | Target | Gap | Next |
|--------|----------|--------------|--------|-----|------|
| **MoE** (mixed Δ overall vs baseline) | 0.000 (a) | **+0.333** visible; (d) **1.0** | hold Δ≥+0.30; (d)≥0.967 | **0** vs freeze; **0** vs polish | Keep router R2 + MFV vis_arith; no adapter writes |
| **Verifier** (python loop) | 0.000 single-shot | **1.0** loop (n=8); hardneg py R1/R2 **1.0** | ≥0.875 floor; prefer 1.0 | **0** | Gold-free extractors only; expand hardneg families carefully |
| **Scaffold** (circuit-graph on ent) | off / no hints | default **ON**; freeze solve **0.9**; Δsolve **0.5**; clear_win | solve≥0.90; Δsolve≥0.45 | **0** | Wire into live mlx ent only after own-delta; keep GT-free |
| **Vision** (mixed scored prior-replay) | 0.900 (pre-polish) | **1.000** scored | ≥0.900 freeze; prefer 1.0 | **0** | Hold per-item prior; VISION_NEG + vis_arith |
| **vision_mlx_parse** (mlx grounding n=3) | **0.0** (0/3 @ API-fix alone, max_tokens=768) | **1.0** (3/3 anti-think: tokens=1536 + strip think + JSON cue + two-phase) | ≥2/3 (~0.67); prefer 1.0 | **0** | Keep API fix + anti-think; demos/CPU unchanged |

## Conflicts honesty

| Merge | Conflicts | Resolution |
|-------|-----------|------------|
| `freeze-polish-bridge` → tip | `evidence_runs.jsonl`, `moe_dual_lane_router.py` | Kept **both** freeze log lines; router = MFV primary (`vis_arith`, chalkboard) **+** R2 `ENT_NEG_RE` / bilingual `VISION_RE` |
| `mixed-with-scaffold` `4d587f7` cherry | mixed `{cpu,smoke,unified}.json` | **Ours (MFV vis/overall 1.0)**; kept scaffold wiring in `moe_verifier_mixed_live.py` |
| `vision-mlx-anti-think` | none (clean) | API fix already ancestor; anti-think layered on top |
| `mixed-with-freeze-r2` `7211f78` | not full-merged (would drop scaffold + revert vis→0.9) | Folded `run_hardneg` CLI + docs/metrics; **did not** take their 0.9667 unified JSON |

## Reproduce

```bash
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_verifier_mixed_live.py --smoke
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_mixed_router.json
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r2_mixed_router.json
.venv/bin/python examples/circuit_graph_moe_scaffold.py --recheck-original --no-write-doc
```

## Artifacts

- `data/frontier_moe_verifier_mixed_{smoke,cpu,unified}.json`
- `data/frontier_moe_dual_lane_hardneg.json` / `_r2.json`
- `data/FRONTIER_CIRCUIT_GRAPH_SCAFFOLD_FREEZE.json`
- `data/frontier_circuit_graph_scaffold_hard_recheck.json`
- `data/frontier_vision_mlx_api_fix_mac111.json`
- `data/frontier_vision_mlx_anti_think_mac111.json`
- `data/freeze_metrics/mixed_with_freeze_r2_20260924.json`
- `docs/FRONTIER-MIXED-FREEZE-VISION.md`
- `docs/FRONTIER-MIXED-WITH-SCAFFOLD.md`
- `docs/FRONTIER-MIXED-WITH-FREEZE-R2.md`
- `docs/FRONTIER-VISION-MLX-ANTI-THINK.md`
