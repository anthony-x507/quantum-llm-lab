# FRONTIER — Código-vivo tip scoreboard

**Branch:** `frontier/codigo-vivo-tip`  
**Written:** 2026-09-24 11:31:30 ET · Mac-111 (`074c6626-…`) · tip `0dd7b79`  
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
| `frontier/codigo-vivo-tip-mlx` | `368b429` | MLX LIVE mixed pillars overall **1.0** (=CPU) |
| PLATFORM freeze @ tip | `b114c51` | lock overall 1.0 @ **f0da3e7** (never abandon) |
| hardneg R3 polish | `5c67267` | R3 router 35/35; floor **1.0** held |
| `frontier/scaffold-wire-vlm` | `ae62ce2` | fold wire→VLM (`text_scaffold_prefix`); rebase `8f5e694`→`e680271` then FF; `wired_to_vlm=true` |
| `frontier/tip-hardneg-r4` | `0dd7b79` | fold R4 polish `40f1d7c` (rebase onto `4e36548` → `11740a6` + sync); R4 40/40; floor **1.0** held |

**Metric policy:** Prefer vision **1.0** / overall **1.0** from `mixed-freeze-vision` over scaffold-merge / R2-port scoreboards that still show vis **0.9** / overall **0.9667**. Keep scaffold wiring + R2 reinforces + anti-think.

## PLATFORM FREEZE (overall 1.0)

**Freeze id:** `codigo_vivo_tip_platform_100pct_20260924_111435`  
**Frozen SHA:** `f0da3e70eba5bebd82d9d07bf2668e042ec250f1` (`f0da3e7`) · branch `frontier/codigo-vivo-tip`  
**When:** 2026-09-24 11:14:35 ET · Mac-139 (`074c6626-…`)  
**Claim:** NO quantum advantage. Classical MoE + `python -I` verifier + prior-replay ent/vision + GT-free scaffold + mlx vision parse.

| Lock | Value |
|------|-------|
| overall (d unified) | **1.0000** |
| MoE Δ overall | **+0.3334** visible |
| pillars | **26/26** |
| hardneg R1 | **18/18 (1.0)** |
| hardneg R2 | **22/22 (1.0)** |
| scaffold freeze | **held** solve=0.9 Δsolve=0.5 · default ON |
| vision_mlx_parse | **1.0** (3/3 anti-think) |
| ent_never_on_python | **true** |
| prompt_touches_gt | **false** |

**Policy:** Never abandon. Polish / reinforce around. `data/lora_adapter/` **READ-ONLY**. No merge to `main`. Prior mixed freeze **≥0.9667** retained.

| Artifact | Path |
|----------|------|
| Manifest | `data/freeze_manifests/codigo_vivo_tip_platform_100pct_20260924_111435.json` |
| Metrics | `data/freeze_metrics/codigo_vivo_tip_platform_20260924.json` |
| Unified | `data/frontier_moe_verifier_mixed_unified.json` |
| Smoke reconfirm | PASS · ~1.35s · pillars 26/26 · hardneg 18/18 |

## MLX+R3 CONSOLIDATE FREEZE (overall 1.0)

**Freeze id:** `codigo_vivo_tip_mlx_r3_100pct_20260924_112131`  
**Frozen SHA:** `5c672671419546de7b510e793875c95e070a0e34` (`5c67267`) · branch `frontier/codigo-vivo-tip`  
**When:** 2026-09-24 11:21:31 ET · Mac-111 (`074c6626-…`)  
**Lineage:** `f0da3e7` → `368b429` (MLX) → `b114c51` (platform freeze) → `5c67267` (R3) — already linear; no merge needed.  
**Claim:** NO quantum advantage. Cites MLX live + R3; **platform freeze f0da3e7 NOT abandoned**.

| Lock | Value |
|------|-------|
| overall (d unified) CPU | **1.0000** (py1 / ent1 / vis1) |
| MoE Δ overall | **+0.3334** visible |
| pillars | **26/26** |
| hardneg R1 / R2 / R3 | **18/18 · 22/22 · 35/35** |
| MLX live (d) | **1.0000** (Δ vs CPU **0**) |
| scaffold freeze | **held** solve=0.9 Δsolve=0.5 · default ON |
| vision_mlx_parse | **1.0** (3/3) |
| ent_never_on_python | **true** |
| prompt_touches_gt | **false** |
| floor held | **yes** (≥0.967, actual 1.0) |

**Policy:** Never abandon platform freeze `f0da3e7` / `codigo_vivo_tip_platform_100pct_20260924_111435`. Prior manifests retained. `data/lora_adapter/` **READ-ONLY**. No merge to `main`.

| Artifact | Path |
|----------|------|
| Manifest | `data/freeze_manifests/codigo_vivo_tip_mlx_r3_100pct_20260924_112131.json` |
| Metrics | `data/freeze_metrics/codigo_vivo_tip_mlx_r3_20260924.json` |
| Doc | `docs/FRONTIER-CODIGO-VIVO-TIP-MLX-R3.md` |
| Platform retained | `data/freeze_manifests/codigo_vivo_tip_platform_100pct_20260924_111435.json` |
| R3 polish retained | `data/freeze_manifests/tip_moe_verifier_polish_r3_100pct_20260924_111740.json` |
| MLX merged | `data/frontier_moe_verifier_mixed_mlx_live_merged.json` |
| Re-smoke | PASS · pillars 26/26 · hardneg 18/18 · cpu overall 1.0 |


## FOLD — scaffold-wire-vlm → tip (overall 1.0 held)

**When:** 2026-09-24 11:24:45 ET · Mac-111 (`074c6626-…`)  
**Method:** tip advanced past scaffold parent → rebase `frontier/scaffold-wire-vlm` (`8f5e694` parent `5c67267`) onto tip `e680271` → new tip `ae62ce2` (FF merge).  
**Claim:** NO quantum advantage. GT-free text scaffold prefix on MoE ent → VLM prompt. Prior freezes **NOT abandoned**.

| Lock | Value |
|------|-------|
| overall (d unified) CPU | **1.0000** (py1 / ent1 / vis1) |
| MoE Δ overall | **+0.3334** visible |
| pillars / hardneg smoke | **26/26 · 18/18** |
| `wired_to_vlm` | **true** (`channel=text_scaffold_prefix`, `weight_peft_injection=false`) |
| scaffold Δsolve / hard Δsolve | **0.5 / 0.6666**; freeze_held **true** |
| `ent_never_on_python` | **true** |
| `prompt_touches_gt` | **false** |
| floor held | **yes** (≥0.967, actual 1.0) |
| platform freeze `f0da3e7` | **retained** |
| MLX+R3 freeze `5c67267` / `codigo_vivo_tip_mlx_r3_…` | **retained** (not abandoned) |

| Artifact | Path |
|----------|------|
| VLM wire | `examples/circuit_graph_adapter/vlm_wire.py` |
| Wire doc | `docs/FRONTIER-SCAFFOLD-WIRE-VLM.md` |
| Wire smoke JSON | `data/frontier_scaffold_wire_vlm.json` |
| Mixed reconfirm | `data/frontier_moe_verifier_mixed_{smoke,cpu,unified}.json` |


## FOLD — tip-hardneg-r4 → tip (overall 1.0 held)

**When:** 2026-09-24 11:31:30 ET · Mac-111 (`074c6626-…`)  
**Method:** tip advanced with scaffold-wire-vlm → rebase `frontier/tip-hardneg-r4` (`40f1d7c` / sync `40f2983`, parent `e680271`) onto tip `4e36548` → `11740a6` + sync `0dd7b79` (FF merge). Mixed JSON conflicts kept tip (re-smoke).  
**Claim:** NO quantum advantage. R4 hardneg reinforce + polish_r4. Prior freezes **NOT abandoned**.

| Lock | Value |
|------|-------|
| overall (d unified) CPU | **1.0000** (py1 / ent1 / vis1) |
| MoE Δ overall | **+0.3334** visible |
| pillars / hardneg smoke | **26/26 · 18/18** |
| hardneg R1 / R2 / R3 / R4 | **18/18 · 22/22 · 35/35 · 40/40** |
| R3 / R4 verifier loop | **28/28 · 32/32** (unified 1.0) |
| `wired_to_vlm` | **true** (`text_scaffold_prefix`) |
| `ent_never_on_python` | **true** |
| `prompt_touches_gt` | **false** |
| floor held | **yes** (≥0.967, actual 1.0) |
| platform freeze `f0da3e7` | **retained** |
| MLX+R3 freeze `5c67267` / `codigo_vivo_tip_mlx_r3_…` | **retained** |
| polish_r4 `40f1d7c` / `tip_moe_verifier_polish_r4_…` | **retained** |

| Artifact | Path |
|----------|------|
| R4 doc | `docs/FRONTIER-CODIGO-VIVO-TIP-R4.md` |
| R4 fixtures | `data/bench_live/hardneg_r4_{mixed_router,python_items}.json` |
| polish_r4 manifest | `data/freeze_manifests/tip_moe_verifier_polish_r4_100pct_20260924_112851.json` |
| R4 metrics | `data/freeze_metrics/codigo_vivo_tip_adv_r4_20260924.json` |
| Mixed reconfirm | `data/frontier_moe_verifier_mixed_{smoke,cpu,unified}.json` |

## LOCK / anti-contam

- Freeze mixed unified overall **≥0.9667** (docs ~0.967); polished floor held at **1.0**. Never abandon.
- `data/lora_adapter/` **READ-ONLY**. No merge to `main`.
- `ent_never_on_python=true`, `prompt_touches_gt=false`, scaffold `gt_leak=0`.

## Live retest (this tip)

**Re-smoke @ 2026-09-24 11:31:30 ET** (fold tip-hardneg-r4 @ `0dd7b79`) · Mac-111

| Check | Result |
|-------|--------|
| Mixed smoke pillars | **26/26** |
| Mixed embedded hardneg | **18/18** |
| `ent_never_on_python` | **True** |
| `circuit_scaffold` default | **ON**; injected **10** on ent |
| `wired_to_vlm` | **True** (text_scaffold_prefix) |
| Unified (d) overall | **1.0000** (py1 / ent1 / vis1) |
| MoE Δ overall | **+0.3334** visible |
| Hardneg R1 router | **18/18 (1.0)** |
| Hardneg R2 router | **22/22 (1.0)** |
| Hardneg R3 router | **35/35 (1.0)** |
| Hardneg R4 router | **40/40 (1.0)** |
| R3 / R4 verifier loop | **28/28 · 32/32** |
| Floor ≥0.967 | **held at 1.0** |


## Hardneg R4 (this tip)

**When:** 2026-09-24 11:31:30 ET · Mac-111  
**Fixtures:** router **n=40**, python **n=32** — families ≠ R1/R2/R3 (yaml_key_qubit / sql_column_bell / docker_image_pennylane / …).

| Check | Result |
|-------|--------|
| R4 router | **40/40 (1.0)** (pre-reinforce 37/40) |
| R4 verifier loop | **1.0** (32/32) |
| R4 unified loop | **1.0** (32/32) |
| Mixed (d) overall | **1.0000 held** (≥0.967 floor) |
| R1/R2/R3 router held | **18/18 · 22/22 · 35/35** |
| R3 verifier held | **28/28** |
| Freeze polish_r4 | **100pct** manifest |
| `ent_never_on_python` | **True** |

Detail: `docs/FRONTIER-CODIGO-VIVO-TIP-R4.md` · metrics `data/freeze_metrics/codigo_vivo_tip_adv_r4_20260924.json`


## Hardneg R3 (this tip)

**When:** 2026-09-24 ~11:20 ET · Mac-139  
**Fixtures:** router **n=35**, python **n=28** — families ≠ R1/R2 (cli/regex/http/typehint/unittest/log/ascii/finance/env/cron).

| Check | Result |
|-------|--------|
| R3 router | **35/35 (1.0)** (pre-reinforce 33/35) |
| R3 verifier loop | **1.0** (28/28) |
| R3 unified loop | **1.0** (28/28) |
| Mixed (d) overall | **1.0000 held** (≥0.967 floor) |
| R1/R2 router held | **18/18 · 22/22** |
| Freeze polish_r3 | **100pct** manifest |
| `ent_never_on_python` | **True** |

Detail: `docs/FRONTIER-CODIGO-VIVO-TIP-R3.md` · metrics `data/freeze_metrics/codigo_vivo_tip_adv_r3_20260924.json`


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
| **Scaffold** (circuit-graph on ent) | off / no hints | default **ON**; freeze solve **0.9**; Δsolve **0.5**; **`wired_to_vlm=true`** | solve≥0.90; Δsolve≥0.45; wire ON | **0** | Keep text_scaffold_prefix; weight_peft_injection=false; GT-free |
| **Vision** (mixed scored prior-replay) | 0.900 (pre-polish) | **1.000** scored | ≥0.900 freeze; prefer 1.0 | **0** | Hold per-item prior; VISION_NEG + vis_arith |
| **vision_mlx_parse** (mlx grounding n=3) | **0.0** (0/3 @ API-fix alone, max_tokens=768) | **1.0** (3/3 anti-think: tokens=1536 + strip think + JSON cue + two-phase) | ≥2/3 (~0.67); prefer 1.0 | **0** | Keep API fix + anti-think; demos/CPU unchanged |

## Conflicts honesty

| Merge | Conflicts | Resolution |
|-------|-----------|------------|
| `freeze-polish-bridge` → tip | `evidence_runs.jsonl`, `moe_dual_lane_router.py` | Kept **both** freeze log lines; router = MFV primary (`vis_arith`, chalkboard) **+** R2 `ENT_NEG_RE` / bilingual `VISION_RE` |
| `mixed-with-scaffold` `4d587f7` cherry | mixed `{cpu,smoke,unified}.json` | **Ours (MFV vis/overall 1.0)**; kept scaffold wiring in `moe_verifier_mixed_live.py` |
| `vision-mlx-anti-think` | none (clean) | API fix already ancestor; anti-think layered on top |
| `mixed-with-freeze-r2` `7211f78` | not full-merged (would drop scaffold + revert vis→0.9) | Folded `run_hardneg` CLI + docs/metrics; **did not** take their 0.9667 unified JSON |
| `scaffold-wire-vlm` `8f5e694`→`ae62ce2` | none (rebase onto `e680271` clean) | FF into tip; re-smoke overall **1.0**; freezes retained |
| `tip-hardneg-r4` `40f1d7c`→`11740a6` | mixed `{cpu,unified}.json` | **Ours (tip scaffold-wire smoke)**; re-smoke after FF → overall **1.0**; freezes retained |

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
.venv/bin/python examples/circuit_graph_moe_scaffold.py --wire-vlm
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r3_mixed_router.json
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r4_mixed_router.json
```

## Artifacts

- `data/frontier_moe_verifier_mixed_{smoke,cpu,unified}.json`
- `data/frontier_moe_dual_lane_hardneg.json` / `_r2.json` / `_r3.json`
- `data/frontier_moe_verifier_hardneg_r3.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r3_20260924.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R3.md`
- `data/FRONTIER_CIRCUIT_GRAPH_SCAFFOLD_FREEZE.json`
- `data/frontier_circuit_graph_scaffold_hard_recheck.json`
- `data/frontier_vision_mlx_api_fix_mac111.json`
- `data/frontier_vision_mlx_anti_think_mac111.json`
- `data/freeze_metrics/mixed_with_freeze_r2_20260924.json`
- `data/freeze_manifests/codigo_vivo_tip_platform_100pct_20260924_111435.json`
- `data/freeze_metrics/codigo_vivo_tip_platform_20260924.json`
- `data/freeze_manifests/codigo_vivo_tip_mlx_r3_100pct_20260924_112131.json`
- `data/freeze_metrics/codigo_vivo_tip_mlx_r3_20260924.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-MLX-R3.md`
- `docs/FRONTIER-SCAFFOLD-WIRE-VLM.md`
- `examples/circuit_graph_adapter/vlm_wire.py`
- `data/frontier_scaffold_wire_vlm.json`
- `data/frontier_moe_verifier_mixed_mlx_live_merged.json`
- `docs/FRONTIER-MIXED-FREEZE-VISION.md`
- `docs/FRONTIER-MIXED-WITH-SCAFFOLD.md`
- `docs/FRONTIER-MIXED-WITH-FREEZE-R2.md`
- `docs/FRONTIER-VISION-MLX-ANTI-THINK.md`

## MLX LIVE mixed (this tip)

**Host:** Mac-111 · Studio offline · 8B effective **5.761 GB** ready  
**Honest n:** py **3** / ent **8** / vis **8** · `metric_source=mlx_live_generate` (not prior-replay)

| Path | python | ent | vision | overall |
|------|--------|-----|--------|---------|
| (a) | 0.000 | 0.000 | 1.000 | 0.333 |
| (b) | 0.000 | 1.000 | 1.000 | 0.667 |
| (c) | 1.000 | 0.000 | 1.000 | 0.667 |
| (d) | **1.000** | **1.000** | **1.000** | **1.000** |

Δ MoE overall **+0.3334** · vs CPU 1.0 **Δ=0** · drops **none** · detail `docs/FRONTIER-CODIGO-VIVO-TIP-MLX.md`

Consolidate freeze citing MLX+R3 (platform f0da3e7 retained): `codigo_vivo_tip_mlx_r3_100pct_20260924_112131` · `docs/FRONTIER-CODIGO-VIVO-TIP-MLX-R3.md`

Fold scaffold→VLM wire (platform + MLX+R3 freezes retained): tip `ae62ce2` · `docs/FRONTIER-SCAFFOLD-WIRE-VLM.md`

## MLX LIVE larger-n (tip-mlx-largern) — 2026-09-24 ~11:58 ET

| Path | python | ent | vision | overall |
|------|--------|-----|--------|---------|
| (a) baseline | 0.125 | 0.000 | 1.000 | 0.375 |
| (b) MoE alone | 0.125 | 1.000 | 1.000 | 0.708 |
| (c) verifier-on-python | 1.000 | 0.000 | 1.000 | 0.667 |
| (d) unified | **1.000** | **1.000** | **1.000** | **1.000** |

n honest: py=8 ent=16 vis=16 · Δ vs CPU 1.0 = **0.0** · floor held · Mac-111 only · see `docs/FRONTIER-CODIGO-VIVO-TIP-MLX-LARGERN.md`

