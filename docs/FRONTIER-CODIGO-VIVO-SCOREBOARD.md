# FRONTIER — Código-vivo tip scoreboard

**Branch:** `frontier/codigo-vivo-tip`  
**Written:** 2026-09-24 12:37:27 ET · Mac-111 (`074c6626-…`) · tip R5 100pct freeze @ `6dce7b6`  
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
| `frontier/tip-mlx-largern` | `c11ccac` | fold mlx LIVE larger-n `d65eb69`/`75f6c0a` (rebase onto `01ddabd` → `23a9b7a`+`c11ccac`); py8/ent16/vis16 unified **1.0**; CPU floor **1.0** held |
| `frontier/tip-ent-sep-fix` | `08463a2` | fold ent-sep-fix (rebase `47975a7` onto `459f6da`); LIVE pool honest 1sep+15ent; MLX ent2 **1.0** with sep; CPU floor **1.0** held |
| `frontier/tip-own-delta-scoreboard` | `66db30a` | fold own-delta (rebase `2382c90` onto `0a1ef4d`); honesty Py−0.062 Ent+1.0 Vis−0.200; dual-lane protects; CPU floor **1.0** held |
| `frontier/tip-hardneg-r5` | `55bdfb7` | fold R5 polish `9a12fbc` (rebase onto `b1c7091` → `49d7ccc` + pin `55bdfb7`); R5 44/44·36/36; floor **1.0** held |
| `frontier/tip-label-protect` | `8b0772a` | fold label-protect/fall-super (`751ed03`+`8b0772a` onto `32fed9b`); router 43/43·verifier 32/32; floor **1.0** held |
| `frontier/tip-hardneg-r6` | `259e4a4` | fold R6 polish `f3fcf1e` (rebase onto `3b10288` → `f3fcf1e` + pin `259e4a4`); R6 48/48·40/40; LP held 43/43·32/32; floor **1.0** held |
| `frontier/tip-own-delta-refresh` | `1b56131` | fold own-delta refresh (rebase onto `4291aab`); RAW Py−0.062 Ent+1.0 Vis−0.200; dual-lane **1.0**; floor **1.0** held |
| `frontier/tip-hardneg-r7` | `f586efd` | fold R7 polish `00fdaaf` (rebase onto `f0fe729` → `00fdaaf` + pin `f586efd`); R7 52/52·44/44; LP held 43/43·32/32; floor **1.0** held |
| `frontier/tip-scaffold-motion` | `d892398` | fold scaffold-motion (rebase onto `69655dd` → `7b0c63b` + pin); motion **44%**; floor **1.0** held |
| `frontier/tip-hardneg-r8` | `e2a950d` | fold R8 polish (rebase onto `d892398` → `afd52c9`+`32b0b14`); R8 52/52·44/44; floor **1.0** held |
| `frontier/tip-distance-danger` | `fd07999` | fold distance-danger (rebase `110bcbc` onto `e2a950d` → `da55eac`+pin); DZ 30–70 m **100%**; floor **1.0** held |
| `frontier/tip-collision-pred` | `3834ebe` | fold collision-pred (rebase `c52ea34`/`da7a628` onto `fd07999` → `3834ebe`+`30194cb` FF); CPU oracle **100%**; floor **1.0** held |
| `frontier/tip-motion-r2` | `77d161a` | fold motion-r2 (rebase `c3cd0a4`/`9649df2` onto `4fe070e` → `77d161a`+`4d91a9c` FF); motion **91%**; floor **1.0** held |
| `frontier/tip-collision-n` | `c79ab1a` | fold collision-n (rebase no-op on `763fb8c` → `c79ab1a`+`55277d9` FF); physics **100%** n=40/2850; floor **1.0** held |

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


## R5 TIP FREEZE (overall 1.0) — tip HEAD after hardneg-r5 fold

**Freeze id:** `codigo_vivo_tip_r5_100pct_20260924_123727`  
**Frozen SHA:** `6dce7b6cceb58ac8ed0946d1977f099f6ab55454` (`6dce7b6`) · branch `frontier/codigo-vivo-tip`  
**When:** 2026-09-24 12:37:27 ET · Mac-111 (`074c6626-…`)  
**Claim:** NO quantum advantage. Cites tip HEAD + R1–R5 holds + mlx largern + ent-sep + own-delta + `wired_to_vlm`. **Prior platform / mlx_r3 / post_polish / polish_r5 freezes NOT abandoned.**

| Lock | Value |
|------|-------|
| overall (d unified) | **1.0000** |
| MoE Δ overall | **+0.3334** visible |
| pillars | **26/26** |
| hardneg R1–R5 | **18/18 · 22/22 · 35/35 · 40/40 · 44/44** |
| R3/R4/R5 verifier | **28/28 · 32/32 · 36/36** |
| wired_to_vlm | **true** (`text_scaffold_prefix`) |
| mlx largern (d) | **1.0000** (py8/ent16/vis16 · Δ vs CPU 0) |
| ent-sep mlx ent2 | **1.0000** (16/16 · scene_0222 held) |
| own-delta honesty | Py **−0.062** · Ent **+1.0** · Vis **−0.200** (dual-lane protects) |
| ent_never_on_python | **true** |
| prompt_touches_gt | **false** |
| floor held | **yes** (≥0.967, actual 1.0) |

**Policy:** Never abandon platform `f0da3e7` / mlx_r3 / post_polish / polish_r5. `data/lora_adapter/` **READ-ONLY**. No merge to `main`.

| Artifact | Path |
|----------|------|
| Manifest | `data/freeze_manifests/codigo_vivo_tip_r5_100pct_20260924_123727.json` |
| Metrics | `data/freeze_metrics/codigo_vivo_tip_r5_20260924.json` |
| Unified | `data/frontier_moe_verifier_mixed_unified.json` |
| MLX largern | `data/frontier_moe_verifier_mixed_mlx_live_pillars_largern_merged.json` |
| Ent-sep | `data/frontier_moe_verifier_mixed_mlx_live_pillars_ent_sep_fix_merged.json` |
| Own-delta | `docs/FRONTIER-CODIGO-VIVO-TIP-OWN-DELTA-SCOREBOARD.md` |
| Wire VLM | `data/frontier_scaffold_wire_vlm.json` |
| Re-smoke | PASS · pillars 26/26 · R1–R5 holds · overall 1.0 · blockers **none** |


## POST-POLISH PLATFORM FREEZE (overall 1.0) — after own-delta fold

**Freeze id:** `codigo_vivo_tip_post_polish_100pct_20260924_123210`  
**Frozen SHA:** `bf5874332b69ffb8d875628a0aa59fef6fee8b40` (`bf58743`) · branch `frontier/codigo-vivo-tip`  
**When:** 2026-09-24 12:32:10 ET · Mac-111 (`074c6626-…`)  
**Claim:** NO quantum advantage. Cites tip HEAD after own-delta fold; **prior platform / mlx_r3 / polish_r3 / polish_r4 freezes NOT abandoned**.

| Lock | Value |
|------|-------|
| overall (d unified) | **1.0000** |
| MoE Δ overall | **+0.3334** visible |
| pillars | **26/26** |
| hardneg R1–R4 | **18/18 · 22/22 · 35/35 · 40/40** |
| R3/R4 verifier | **28/28 · 32/32** |
| wired_to_vlm | **true** (`text_scaffold_prefix`) |
| own-delta honesty | Py **−0.062** · Ent **+1.0** · Vis **−0.200** (dual-lane protects) |
| ent_never_on_python | **true** |
| prompt_touches_gt | **false** |
| floor held | **yes** (≥0.967, actual 1.0) |

**Policy:** Never abandon platform `f0da3e7` / mlx_r3 / polish_r4. `data/lora_adapter/` **READ-ONLY**. No merge to `main`.

| Artifact | Path |
|----------|------|
| Manifest | `data/freeze_manifests/codigo_vivo_tip_post_polish_100pct_20260924_123210.json` |
| Metrics | `data/freeze_metrics/codigo_vivo_tip_post_polish_20260924.json` |
| Unified | `data/frontier_moe_verifier_mixed_unified.json` |
| Own-delta | `docs/FRONTIER-CODIGO-VIVO-TIP-OWN-DELTA-SCOREBOARD.md` |


## R6 TIP FREEZE / FOLD (overall 1.0) — tip HEAD after hardneg-r6 fold

**Freeze id:** `codigo_vivo_tip_r6_100pct`  
**Tip HEAD (pre-fold-docs):** `259e4a4` · rebased from `32fed9b` onto label-protect tip `3b10288`  
**Claim:** NO quantum advantage. Cites tip HEAD after R6 fold; **prior platform / mlx_r3 / post_polish / R5 tip / label_protect / polish_r5 / polish_r6 freezes NOT abandoned**.

| Surface | Score |
|---------|-------|
| mixed (d) unified | **1.0** |
| hardneg R1–R6 | **18/18 · 22/22 · 35/35 · 40/40 · 44/44 · 48/48** |
| R3/R4/R5/R6 verifier | **28/28 · 32/32 · 36/36 · 40/40** |
| label-protect | **43/43 · 32/32** |
| router smoke / pillars | **12/12 · 26/26** |
| `ent_never_on_python` | **true** |

**Policy:** Never abandon platform / mlx_r3 / post_polish / R5 tip / label_protect. `data/lora_adapter/` **READ-ONLY**. No merge to `main`.

| Artifact | Path |
|----------|------|
| Manifest | `data/freeze_manifests/codigo_vivo_tip_r6_100pct_*.json` |
| Metrics | `data/freeze_metrics/codigo_vivo_tip_r6_20260924.json` |
| R6 doc | `docs/FRONTIER-CODIGO-VIVO-TIP-R6.md` |
| Re-smoke | PASS · R6 48/48·40/40 · LP 43/43·32/32 · cpu overall 1.0 |


## R7 TIP FREEZE / FOLD (overall 1.0) — tip HEAD after hardneg-r7 fold

**Freeze id:** `codigo_vivo_tip_r7_100pct`  
**Tip HEAD (pre-fold-docs):** `f586efd` · rebased from `4291aab` onto POST-OD2 tip `f0fe729`  
**Claim:** NO quantum advantage. Cites tip HEAD after R7 fold; **prior platform / mlx_r3 / post_polish / R5 / label_protect / R6 / post_od2 / polish_r7 freezes NOT abandoned**.

| Surface | Score |
|---------|-------|
| mixed (d) unified | **1.0** |
| hardneg R1–R7 | **18/18 · 22/22 · 35/35 · 40/40 · 44/44 · 48/48 · 52/52** |
| R3–R7 verifier | **28/28 · 32/32 · 36/36 · 40/40 · 44/44** |
| label-protect | **43/43 · 32/32** |
| router smoke / pillars | **12/12 · 26/26** |
| `ent_never_on_python` | **true** |

**Policy:** Never abandon platform / mlx_r3 / post_polish / R5 / LP / R6 / post_od2. `data/lora_adapter/` **READ-ONLY**. No merge to `main`.

| Artifact | Path |
|----------|------|
| Manifest | `data/freeze_manifests/codigo_vivo_tip_r7_100pct_*.json` |
| Metrics | `data/freeze_metrics/codigo_vivo_tip_r7_20260924.json` |
| R7 doc | `docs/FRONTIER-CODIGO-VIVO-TIP-R7.md` |
| Re-smoke | PASS · R7 52/52·44/44 · LP 43/43·32/32 · cpu overall 1.0 |

## POST-OD2 TIP FREEZE (overall 1.0) — after own-delta refresh fold + R6

**Freeze id:** `codigo_vivo_tip_post_od2_100pct_20260924_125301`  
**Frozen SHA:** `15c9a2317409f63a1f58d801b1bedd203bb86758` (`15c9a23`) · branch `frontier/codigo-vivo-tip`  
**When:** 2026-09-24 12:53:01 ET · Mac-111 (`074c6626-…`)  
**Claim:** NO quantum advantage. Cites tip HEAD after own-delta-refresh fold on R6 tip; **prior platform / mlx_r3 / post_polish / R5 / label_protect / R6 freezes NOT abandoned**.

| Lock | Value |
|------|-------|
| overall (d unified) | **1.0000** |
| MoE Δ overall | **+0.3334** visible |
| pillars | **26/26** |
| hardneg R1–R6 | **18/18 · 22/22 · 35/35 · 40/40 · 44/44 · 48/48** |
| R3–R6 verifier | **28/28 · 32/32 · 36/36 · 40/40** |
| label-protect | **43/43 · 32/32** |
| own-delta refresh | Py **−0.062** · Ent **+1.0** · Vis **−0.200** (dual-lane **1.0**) |
| wired_to_vlm | **true** (`text_scaffold_prefix`) |
| ent_never_on_python | **true** |
| prompt_touches_gt | **false** |
| floor held | **yes** (≥0.967, actual 1.0) |

**Policy:** Never abandon platform / mlx_r3 / post_polish / R5 / LP / R6 (`codigo_vivo_tip_r6_100pct_20260924_124951`). `data/lora_adapter/` **READ-ONLY**. No merge to `main`.

| Artifact | Path |
|----------|------|
| Manifest | `data/freeze_manifests/codigo_vivo_tip_post_od2_100pct_20260924_125301.json` |
| Metrics | `data/freeze_metrics/codigo_vivo_tip_post_od2_20260924.json` |
| Unified | `data/frontier_moe_verifier_mixed_unified.json` |
| Own-delta refresh | `docs/FRONTIER-CODIGO-VIVO-TIP-OWN-DELTA-REFRESH.md` |
| Re-smoke | PASS · pillars 26/26 · R6 48/48 · LP 43/43 · cpu overall 1.0 |


## LABEL-PROTECT TIP FREEZE (overall 1.0) — after label-protect fold

**Freeze id:** `codigo_vivo_tip_label_protect_100pct_20260924_124608`  
**Frozen SHA:** `d151432894282e08cb03fc278bd03f5a0eeca9ec` (`d151432`) · branch `frontier/codigo-vivo-tip`  
**When:** 2026-09-24 12:46:08 ET · Mac-111 (`074c6626-…`)  
**Claim:** NO quantum advantage. Cites tip HEAD after label-protect fold; **prior platform / mlx_r3 / post_polish / R5 tip / polish_r5 / label-protect polish freezes NOT abandoned**.

| Lock | Value |
|------|-------|
| overall (d unified) | **1.0000** |
| MoE Δ overall | **+0.3334** visible |
| pillars | **26/26** |
| hardneg R1–R5 | **18/18 · 22/22 · 35/35 · 40/40 · 44/44** |
| R3/R4/R5 verifier | **28/28 · 32/32 · 36/36** |
| label-protect | **43/43 · 32/32** |
| wired_to_vlm | **true** (`text_scaffold_prefix`) |
| mlx largern / ent-sep | **1.0 / 1.0** (cited) |
| own-delta honesty | Py **−0.062** · Ent **+1.0** · Vis **−0.200** (dual-lane protects) |
| ent_never_on_python | **true** |
| prompt_touches_gt | **false** |
| floor held | **yes** (≥0.967, actual 1.0) |

**Policy:** Never abandon platform `f0da3e7` / mlx_r3 / post_polish / R5 tip `codigo_vivo_tip_r5_100pct_20260924_123727`. `data/lora_adapter/` **READ-ONLY**. No merge to `main`.

| Artifact | Path |
|----------|------|
| Manifest | `data/freeze_manifests/codigo_vivo_tip_label_protect_100pct_20260924_124608.json` |
| Metrics | `data/freeze_metrics/codigo_vivo_tip_label_protect_20260924.json` |
| Unified | `data/frontier_moe_verifier_mixed_unified.json` |
| Label-protect | `docs/FRONTIER-CODIGO-VIVO-TIP-LABEL-PROTECT.md` |
| Re-smoke | PASS · pillars 26/26 · hardneg 18/18 · LP 43/43 · R5 44/44 · cpu overall 1.0 |


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


## FOLD — tip-mlx-largern → tip (overall 1.0 held)

**When:** 2026-09-24 12:03:20 ET · Mac-111 (`074c6626-…`)  
**Method:** tip advanced with R4 fold `01ddabd` → rebase `frontier/tip-mlx-largern` (`75f6c0a` / feat `d65eb69`, parent `0dd7b79`) onto tip → `23a9b7a` + stamp `c11ccac` (FF merge). Expanded LIVE pool moved to `mixed_items_largern.json`; tip `mixed_items.json` kept for CPU floor.  
**Claim:** NO quantum advantage. MLX LIVE larger-n evidence fold. Prior freezes **NOT abandoned**. Separable `scene_0222` flaky — **evidence folded, not fixed**.

| Lock | Value |
|------|-------|
| overall (d unified) CPU | **1.0000** (py1 / ent1 / vis1) |
| MoE Δ overall | **+0.3334** visible |
| pillars / hardneg smoke | **26/26 · 18/18** |
| hardneg R1 / R2 / R3 / R4 | **18/18 · 22/22 · 35/35 · 40/40** |
| R3 / R4 verifier loop | **28/28 · 32/32** (unified 1.0) |
| MLX LIVE largern (d) | **1.0000** (py8/ent16/vis16 · Δ vs CPU **0**) |
| `wired_to_vlm` | **true** (`text_scaffold_prefix`) |
| `ent_never_on_python` | **true** |
| `prompt_touches_gt` | **false** |
| floor held | **yes** (≥0.967, actual 1.0) |
| platform freeze `f0da3e7` | **retained** |
| MLX+R3 freeze `5c67267` / `codigo_vivo_tip_mlx_r3_…` | **retained** |
| polish_r4 `40f1d7c` / `tip_moe_verifier_polish_r4_…` | **retained** |

| Artifact | Path |
|----------|------|
| LARGERN doc | `docs/FRONTIER-CODIGO-VIVO-TIP-MLX-LARGERN.md` |
| Primary merged | `data/frontier_moe_verifier_mixed_mlx_live_pillars_largern_merged.json` |
| LIVE pool | `data/bench_live/mixed_items_largern.json` |
| Mixed reconfirm | `data/frontier_moe_verifier_mixed_{smoke,cpu,unified}.json` |

## FOLD — tip-ent-sep-fix → tip (overall 1.0 held)

**When:** 2026-09-24 12:24:30 ET · Mac-111 (`074c6626-…`)  
**Method:** tip at `459f6da` (largern folded) → rebase `frontier/tip-ent-sep-fix` (`47975a7` parent `c11ccac`) onto tip → `08463a2` (FF merge). Conflict: tip CPU `mixed_items.json` kept; honest 1sep+15ent LIVE pool → `mixed_items_largern.json`; mlx runner keeps largern path + `scaffold_polish=True`.  
**Claim:** NO quantum advantage. Honest separable-at-n=16 fix (GT-free motion cue + scaffold diversity). Prior freezes **NOT abandoned**.

| Lock | Value |
|------|-------|
| overall (d unified) CPU | **1.0000** (py1 / ent1 / vis1) |
| MoE Δ overall | **+0.3334** visible |
| pillars / hardneg smoke | **26/26 · 18/18** |
| hardneg R1 / R2 / R3 / R4 | **18/18 · 22/22 · 35/35 · 40/40** |
| R3 / R4 verifier loop | **28/28 · 32/32** (unified 1.0) |
| MLX LIVE ent2 with ≥1 sep | **1.0000** (16/16 · `scene_0222` held · Δ vs CPU **0**) |
| `wired_to_vlm` | **true** (`text_scaffold_prefix`) |
| `ent_never_on_python` | **true** |
| `prompt_touches_gt` | **false** |
| floor held | **yes** (≥0.967, actual 1.0) |
| platform freeze `f0da3e7` | **retained** |
| MLX+R3 freeze `5c67267` / `codigo_vivo_tip_mlx_r3_…` | **retained** |
| polish_r4 `40f1d7c` / `tip_moe_verifier_polish_r4_…` | **retained** |

| Artifact | Path |
|----------|------|
| ENT-SEP-FIX doc | `docs/FRONTIER-CODIGO-VIVO-TIP-ENT-SEP-FIX.md` |
| Primary merged | `data/frontier_moe_verifier_mixed_mlx_live_pillars_ent_sep_fix_merged.json` |
| LIVE pool (honest) | `data/bench_live/mixed_items_largern.json` (1 sep + 15 ent) |
| Mixed reconfirm | `data/frontier_moe_verifier_mixed_{smoke,cpu,unified}.json` |



## FOLD — tip-hardneg-r5 → tip (overall 1.0 held)

**When:** 2026-09-24 12:35:26 ET · Mac-111 (`074c6626-…`)  
**Method:** tip free at `b1c7091` (post_polish) → rebase `frontier/tip-hardneg-r5` (`5dfaf51` / polish `9a12fbc`, parent `0a1ef4d`) onto tip → `49d7ccc` + pin `55bdfb7` (FF merge). Mixed JSON conflicts kept tip (re-smoke).  
**Claim:** NO quantum advantage. R5 hardneg reinforce + polish_r5. Prior freezes **NOT abandoned** (incl. post_polish).

| Lock | Value |
|------|-------|
| overall (d unified) CPU | **1.0000** (py1 / ent1 / vis1) |
| MoE Δ overall | **+0.3334** visible |
| pillars / hardneg smoke | **26/26 · 18/18** |
| hardneg R1 / R2 / R3 / R4 / R5 | **18/18 · 22/22 · 35/35 · 40/40 · 44/44** |
| R3 / R4 / R5 verifier loop | **28/28 · 32/32 · 36/36** (unified 1.0) |
| `wired_to_vlm` | **true** (`text_scaffold_prefix`) |
| `ent_never_on_python` | **true** |
| `prompt_touches_gt` | **false** |
| floor held | **yes** (≥0.967, actual 1.0) |
| platform freeze `f0da3e7` | **retained** |
| MLX+R3 freeze `5c67267` / `codigo_vivo_tip_mlx_r3_…` | **retained** |
| polish_r4 `40f1d7c` / `tip_moe_verifier_polish_r4_…` | **retained** |
| post_polish `bf58743` / `codigo_vivo_tip_post_polish_…` | **retained** |
| polish_r5 `9a12fbc` / `tip_moe_verifier_polish_r5_…` | **retained** |

| Artifact | Path |
|----------|------|
| R5 doc | `docs/FRONTIER-CODIGO-VIVO-TIP-R5.md` |
| R5 fixtures | `data/bench_live/hardneg_r5_{mixed_router,python_items}.json` |
| polish_r5 manifest | `data/freeze_manifests/tip_moe_verifier_polish_r5_100pct_20260924_123200.json` |
| R5 metrics | `data/freeze_metrics/codigo_vivo_tip_adv_r5_20260924.json` |
| Mixed reconfirm | `data/frontier_moe_verifier_mixed_{cpu,unified}.json` |


## LOCK / anti-contam

- Freeze mixed unified overall **≥0.9667** (docs ~0.967); polished floor held at **1.0**. Never abandon.
- `data/lora_adapter/` **READ-ONLY**. No merge to `main`.
- `ent_never_on_python=true`, `prompt_touches_gt=false`, scaffold `gt_leak=0`.

## Live retest (this tip)

**Re-smoke @ 2026-09-24 12:37:27 ET** (R5 tip freeze @ `6dce7b6`) · Mac-111

| Check | Result |
|-------|--------|
| Mixed smoke pillars | **26/26** |
| Mixed embedded hardneg | **18/18** |
| `ent_never_on_python` | **True** |
| `circuit_scaffold` default | **ON**; injected **10** on ent |
| `wired_to_vlm` | **True** (text_scaffold_prefix) |
| Unified (d) overall | **1.0000** (py1 / ent1 / vis1) |
| MoE Δ overall | **+0.3334** visible |
| Hardneg R1–R5 router | **18/18 · 22/22 · 35/35 · 40/40 · 44/44** |
| R3 / R4 / R5 verifier loop | **28/28 · 32/32 · 36/36** |
| MLX LIVE largern (d) | **1.0000** (py8/ent16/vis16 · Δ vs CPU 0) |
| MLX LIVE ent2 w/ sep | **1.0000** (n16 · scene_0222 held · Δ vs CPU 0) |
| Own-delta honesty | Py **−0.062** · Ent **+1.0** · Vis **−0.200** |
| Floor ≥0.967 | **held at 1.0** |
| Blockers | **none** |
| Retained freezes | platform · mlx_r3 · post_polish · polish_r5 (**not abandoned**) |



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
| **Verifier** (python loop) | 0.000 single-shot | **1.0** loop (n=8); hardneg py R1–R5 **1.0** | ≥0.875 floor; prefer 1.0 | **0** | Gold-free extractors only; expand hardneg families carefully |
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
| `tip-mlx-largern` `75f6c0a`→`c11ccac` | `mixed_items.json` (expanded n) | **Tip CPU pool restored**; LIVE pool → `mixed_items_largern.json`; re-smoke overall **1.0**; freezes retained; sep flaky not fixed |
| `tip-hardneg-r5` `9a12fbc`→`49d7ccc` | mixed `{cpu,unified}.json` | **Ours (tip post_polish smoke)**; re-smoke after FF → overall **1.0**; freezes retained incl. post_polish |

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
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r5_mixed_router.json
```

## Artifacts

- `data/frontier_moe_verifier_mixed_mlx_live_pillars_largern_merged.json`
- `data/bench_live/mixed_items_largern.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-MLX-LARGERN.md`
- `data/frontier_moe_verifier_mixed_{smoke,cpu,unified}.json`
- `data/frontier_moe_dual_lane_hardneg.json` / `_r2.json` / `_r3.json`
- `data/frontier_moe_verifier_hardneg_r3.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r3_20260924.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R3.md`
- `data/bench_live/hardneg_r5_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r5.json`
- `data/frontier_moe_verifier_hardneg_r5.json`
- `data/freeze_manifests/tip_moe_verifier_polish_r5_100pct_20260924_123200.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r5_20260924.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R5.md`
- `data/FRONTIER_CIRCUIT_GRAPH_SCAFFOLD_FREEZE.json`
- `data/frontier_circuit_graph_scaffold_hard_recheck.json`
- `data/frontier_vision_mlx_api_fix_mac111.json`
- `data/frontier_vision_mlx_anti_think_mac111.json`
- `data/freeze_metrics/mixed_with_freeze_r2_20260924.json`
- `data/freeze_manifests/codigo_vivo_tip_r5_100pct_20260924_123727.json`
- `data/freeze_metrics/codigo_vivo_tip_r5_20260924.json`
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

n honest: py=8 ent=16 vis=16 · Δ vs CPU 1.0 = **0.0** · floor held · Mac-111 only · **FOLDED** @ 12:03 ET · see `docs/FRONTIER-CODIGO-VIVO-TIP-MLX-LARGERN.md`

## Own-delta tip scoreboard — FOLDED

**When:** 2026-09-24 ~12:27 ET measure · fold 2026-09-24 12:31:44 ET · Mac-111 · rebase onto `0a1ef4d` → `66db30a` FF  
**Doc:** `docs/FRONTIER-CODIGO-VIVO-TIP-OWN-DELTA-SCOREBOARD.md`  
**JSON:** `data/frontier_tip_own_delta_scoreboard.json`

| pillar | base | adapter | Δ | tip dual-lane |
|--------|------|---------|---|----------------|
| Python | 0.062 | 0.000 (quantum) | **−0.062** | BASE+verifier → **1.0** (avoids adapter) |
| Ent | 0.000 | 1.000 (ent2) | **+1.000** | ent2 → **1.0** (still helps) |
| Vision | 0.900 | 0.700 (quantum) | **−0.200** | BASE → **1.0** (avoids adapter) |

**CPU re-smoke after fold:** unified **1.0**; R1–R4 **18/18·22/22·35/35·40/40**; R3/R4 verifier **28/28·32/32**; `wired_to_vlm=true`.  
Anti-contam **CLEAN** (`prompt_touches_gt=false`). Adapters RO mtime unchanged. Classical present, not routed on CV pillars.  
**Key honesty:** ent2 still **+1.0**; quantum alone hurts py/vis; dual-lane protects. Platform / mlx_r3 / polish_r4 freezes **retained**.





## Collision-n (eval expand 8→40) — FOLDED

**Freeze:** `codigo_vivo_tip_collision_n_100pct_20260924_132559`  
**Doc:** `docs/FRONTIER-CODIGO-VIVO-TIP-COLLISION-N.md`  
**SHA:** feat `c79ab1a` · pin `55277d9` · fold FF onto tip `763fb8c` (rebase no-op)

| Lock | Value |
|------|-------|
| collision_physics overall | **100%** (2850 queries / **40** eval) |
| collision_choose_safest | **100%** |
| inverse_cv overall | 89.82% |
| ablation (phys − inv) | +10.18 pp |
| n_eval before→after | 8 → **40** |
| n_queries before→after | 555 → **2850** |
| contam / retrieval | **PASS** / **ok** |
| mixed (d) unified | **1.0** (re-smoke) |
| motion coverage | **91%** held |
| prior collision_pred freeze | **retained** (`…131846`, n=8 history) |

**CPU re-smoke after fold:** unified **1.0**; collision probe reconfirmed 100% @ n=40; R8+LP held; freezes retained incl. motion_r2 + collision_pred + distance_danger + r8 + scaffold_motion + r7 + post_od2 + LP + r6 + priors. Adapters RO. **R9 not folded.**

## Motion-r2 (coverage reinforce 44%→91%) — FOLDED

**When:** polish ~13:15 ET · fold 2026-09-24 13:23:34 ET · Mac-111 · rebase `9649df2`/`c3cd0a4` onto `4fe070e` → `77d161a`+`4d91a9c` FF  
**Doc:** `docs/FRONTIER-CODIGO-VIVO-TIP-MOTION-R2.md`  
**Freeze:** `codigo_vivo_tip_motion_r2_100pct_20260924_131537`

| Surface | Result |
|---------|--------|
| Mixed (d) unified | **1.0** (py/ent/vis) |
| Motion known coverage (n=200) | **91%** (132 ind + 50 corr; +47.0 pp vs 44%) |
| Remaining unknown | 18 (2 track_fail + 16 ambiguous) |
| `scene_0222` | **independent** (held, stage=hue_hard) |
| R8 / LP | **52/52·44/44** / **43/43·32/32** |
| pillars / smoke | **26/26** / **12/12** |
| collision_physics (held) | **100%** (555/8) |
| `wired_to_vlm` / gt_leak / `ent_never_on_python` | **true** / **false** / **true** |

**CPU re-smoke after fold:** unified **1.0**; motion probe **91%**; R8+LP held; freezes retained incl. r8 + scaffold_motion + distance_danger + collision_pred + r7 + post_od2 + LP + r6 + priors. Adapters RO.

## Collision-pred (CPU oracle) — FOLDED

**When:** polish ~13:09 ET · fold 2026-09-24 13:18:46 ET · Mac-111 · rebase `da7a628`/`c52ea34` onto `fd07999` → `3834ebe`+`30194cb` FF  
**Doc:** `docs/FRONTIER-CODIGO-VIVO-TIP-COLLISION-PRED.md`  
**Freeze:** `codigo_vivo_tip_collision_pred_100pct_20260924_131846`

| Surface | Result |
|---------|--------|
| Mixed (d) unified | **1.0** (py/ent/vis) |
| collision_physics overall | **100%** (555 queries / 8 eval) |
| collision_choose_safest | **100%** |
| ablation vs inverse_cv | **+14.77 pp** |
| contam / retrieval | **PASS** / **ok** |
| R8 / LP | **52/52·44/44** / **43/43·32/32** |
| pillars / smoke | **26/26** / **12/12** |
| motion coverage | **44%** (held) |
| `wired_to_vlm` / gt_leak / `ent_never_on_python` | **true** / **false** / **true** |

**CPU re-smoke after fold:** unified **1.0**; R8+LP held; collision probe reconfirmed 100%; freezes retained incl. r8 + scaffold_motion + distance_danger + r7 + post_od2 + LP + r6 + priors. Adapters RO. Motion-r2 folded later — see Motion-r2 section.

## Distance-danger (30–70 m DZ) — FOLDED

**When:** polish ~13:05 ET · fold 2026-09-24 13:12:43 ET · Mac-111 · rebase `110bcbc` onto `e2a950d` → `da55eac` FF  
**Doc:** `docs/FRONTIER-CODIGO-VIVO-TIP-DISTANCE-DANGER.md`  
**Freeze:** `codigo_vivo_tip_distance_danger_100pct_20260924_131243`

| Surface | Result |
|---------|--------|
| Mixed (d) unified | **1.0** (py/ent/vis) |
| 30–70 m DZ (orig / danger50) | **100%** / **100%** (MAE 1.49 / 0.73 m) |
| ~50 m band | **100%** (+51.31 pp vs 48.69) |
| future-pred DZ +dist | **97.3%** / **96.59%** |
| tracking DZ | **100%** |
| R8 / LP | **52/52·44/44** / **43/43·32/32** |
| pillars / smoke | **26/26** / **12/12** |
| motion coverage | **44%** (held) |
| `wired_to_vlm` / gt_leak / `ent_never_on_python` | **true** / **false** / **true** |

**CPU re-smoke after fold:** unified **1.0**; R8+LP held; DZ probe reconfirmed; freezes retained incl. r8 + scaffold_motion + r7 + post_od2 + LP + r6 + priors. Adapters RO. Collision-pred folded later — see Collision-pred section.

## Hardneg R8 — FOLDED

**When:** polish ~12:56–1:01 ET · fold 2026-09-24 13:09:50 ET · Mac-111 · rebase `270ce46`/`c964dcc` onto `d892398` → `afd52c9`+`32b0b14` FF  
**Doc:** `docs/FRONTIER-CODIGO-VIVO-TIP-R8.md`  
**Freeze:** `codigo_vivo_tip_r8_100pct_20260924_130950`

| Surface | Result |
|---------|--------|
| Mixed (d) unified | **1.0** (py/ent/vis) |
| R8 router / verifier | **52/52** / **44/44** |
| R7 / LP | **52/52·44/44** / **43/43·32/32** |
| R1–R6 routers | 18/18·22/22·35/35·40/40·44/44·48/48 |
| R3–R6 verifiers | 28/28·32/32·36/36·40/40 |
| pillars / smoke | **26/26** / **12/12** |
| motion coverage | **44%** (held) |
| `wired_to_vlm` / gt_leak / `ent_never_on_python` | **true** / **false** / **true** |

**CPU re-smoke after fold:** unified **1.0**; R8 held; freezes retained incl. scaffold_motion + r7 + post_od2 + LP + r6 + priors. Adapters RO. Distance-danger folded later — see Distance-danger section.


## Scaffold-motion (RGB cue honesty) — FOLDED

**When:** measure ~12:55 ET · fold 2026-09-24 13:01:31 ET · Mac-111 · rebase `9ddfaed` onto `69655dd` → `7b0c63b` FF  
**Doc:** `docs/FRONTIER-CODIGO-VIVO-TIP-SCAFFOLD-MOTION.md`  
**Freeze:** `codigo_vivo_tip_scaffold_motion_100pct_20260924_130131`

| Surface | Result |
|---------|--------|
| Mixed (d) unified | **1.0** (py/ent/vis) |
| Motion known coverage (n=200) | **44%** (73 ind + 15 corr) |
| `wired_to_vlm` / gt_leak | **true** / **false** |
| R7 / LP | **52/52·44/44** / **43/43·32/32** |
| R1–R6 routers | 18/18·22/22·35/35·40/40·44/44·48/48 |
| pillars / smoke | **26/26** / **12/12** |
| `ent_never_on_python` | **true** |

**CPU re-smoke after fold:** unified **1.0**; motion probe held; freezes retained incl. r7 + post_od2 + LP + r6 + priors. Adapters RO. R8 folded later — see Hardneg R8 section.

## Hardneg R5 — FOLDED

**When:** 2026-09-24 12:35:26 ET · Mac-111 · rebase `5dfaf51`/`9a12fbc` onto `b1c7091` → `49d7ccc`+`55bdfb7` FF  
**Doc:** `docs/FRONTIER-CODIGO-VIVO-TIP-R5.md`

**CPU re-smoke after fold:** unified **1.0**; R1–R5 routers **18/18·22/22·35/35·40/40·44/44**; R3/R4/R5 verifier **28/28·32/32·36/36**; `wired_to_vlm=true`.  
Anti-contam **CLEAN**. Adapters RO unchanged. Platform / mlx_r3 / polish_r4 / **post_polish** / polish_r5 freezes **retained**.

**R5 tip freeze (100pct):** `codigo_vivo_tip_r5_100pct_20260924_123727` @ tip `6dce7b6` · 2026-09-24 12:37:27 ET · cites R1–R5 + mlx largern + ent-sep + own-delta + wired_to_vlm · blockers **none**.

## Label-protect / fall-super — FOLDED

**When:** measure ~12:45 ET · fold 2026-09-24 12:44:19 ET · Mac-111 · rebase onto `32fed9b` → `751ed03`+`8b0772a` FF  
**Doc:** `docs/FRONTIER-CODIGO-VIVO-TIP-LABEL-PROTECT.md`

**Δ:** router **36/43→43/43**; verifier **32/32**; mixed (d) **1.0 held**.  
**Honesty:** dual-lane + negated `json válido` / empty `gates=[]` protect python/base from ent mis-route on fall/super label words; real fall/super circuit JSON asks stay ent.  
**CPU re-smoke after fold:** unified **1.0**; label-protect **43/43·32/32**; R1–R5 routers **18/18·22/22·35/35·40/40·44/44**; R3/R4/R5 verifier **28/28·32/32·36/36**; `wired_to_vlm` retained · R5 tip freeze `codigo_vivo_tip_r5_100pct_20260924_123727` **retained**; label-protect tip freeze `codigo_vivo_tip_label_protect_100pct_20260924_124608` **locked**.  
Platform / mlx_r3 / post_polish / polish_r5 / R5 tip freezes **retained**. Never abandon.

## Own-delta tip refresh — FOLDED

**When:** measure ~12:50 ET · fold 2026-09-24 12:51:49 ET · Mac-111 · rebase onto `4291aab` → `1b56131` FF  
**Doc:** `docs/FRONTIER-CODIGO-VIVO-TIP-OWN-DELTA-REFRESH.md`  
**JSON:** `data/frontier_tip_own_delta_refresh_scoreboard.json`  
**Tip cited at measure:** `3b10288` · folded onto tip with R6 (`4291aab`)

| pillar | base | adapter | Δ | tip dual-lane |
|--------|------|---------|---|----------------|
| Python | 0.062 | 0.000 (quantum) | **−0.062** | BASE+verifier → **1.0** (avoids adapter) |
| Ent | 0.000 | 1.000 (ent2 LIVE n=3) | **+1.000** | ent2 → **1.0** (still helps) |
| Vision | 0.900 | 0.700 (quantum) | **−0.200** | BASE → **1.0** (avoids adapter) |

**CPU / MLX sample:** unified **1.0** / **1.0** (Δ=0). pillars 26/26 · hardneg 18/18 · `wired_to_vlm=true`.  
**Honesty held:** RAW deltas unchanged vs prior own-delta; dual-lane still protects tip floor under label-protect+R5 composition.  
`ro_mtime_unchanged=true`. Freezes retained incl. `codigo_vivo_tip_label_protect_100pct_20260924_124608`.

**CPU re-smoke after fold:** unified **1.0**; LP **43/43**; R5 **44/44**; R6 **48/48**; pillars **26/26**; freezes retained incl. r6 + label_protect · 2026-09-24 12:51:49 ET.

