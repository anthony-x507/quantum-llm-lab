## 2026-09-24 — fold tip-hardneg-r19 → codigo-vivo-tip
Cherry-pick `f20e327` onto `9c320cb` → fold feat `PENDING`. Conflicts: STATUS+mixed/LP/r7–r12 JSON ours; router/verifier merged R12+R13+R14+R15+R16+R17+R18+R19 gates_ops. Re-smoke R19 **18→52/52** · **44/44** (side 6→52; post-score retained **100%**; tip-local rise_ret ~73.9% of side trail; side rise_pp **88.46** ≥80 → freeze); R18 52/52·44/44; R17 52/52·44/44; pillars 37/37; circ 5/5 cited; mixed (d) 1.0; choose_n n=80 @100% freeze retained; tti-cold ~95% freeze retained (no residual chase); freezes retained incl. r18+r17+tti_cold_fold+r16+choose_safest_n_fold+r15+r14+LP+pillars+circ+future_r3+side polish_r19. Freeze `codigo_vivo_tip_r19_100pct_20260924_154857`. R20+ not folded. Tip vis stays BASE. RO data/lora_adapter/.

- Fold tip-hardneg-r18 → codigo-vivo-tip @ e62cb61 (freeze codigo_vivo_tip_r18_100pct_20260924_154419); R19+ not folded.
- 2026-09-24 ET — fold tip-hardneg-r17 → codigo-vivo-tip; R17 8→52/52 · 44/44; freeze `codigo_vivo_tip_r17_100pct_20260924_153921`; mixed 1.0; R16/tti-cold/choose_n retained; R18+ not folded.
- 2026-09-24 ET — fold tip-tti-cold → codigo-vivo-tip; freeze `codigo_vivo_tip_tti_cold_fold_100pct_20260924_152850`; cold 91.16→94.99 / 91.66→94.82; plateau hold; R17+ not folded.
- 2026-09-24 ET: fold tip-hardneg-r16 → codigo-vivo-tip; R16 11→52/52 · 44/44; freeze `codigo_vivo_tip_r16_100pct_20260924_152253`; choose_n retained; tti-cold/R17+ not folded.
- 2026-09-24 fold tip-choose-safest-n → tip; freeze `codigo_vivo_tip_choose_safest_n_fold_100pct_20260924_151818`; n 40→80 @ physics+choose_safest 100%; R15 52/52 held; mixed 1.0; RO adapters.
- 2026-09-24: fold tip-hardneg-r15 → tip; freeze `codigo_vivo_tip_r15_100pct_20260924_151243` (15→52/52·44/44; R14 52 held; LP 64/64; pillars 37; circ 5/5; mixed 1.0).
- 2026-09-24: fold tip-hardneg-r14 → tip; freeze `codigo_vivo_tip_r14_100pct_20260924_150809` (16→52/52·44/44; LP 64/64; pillars 37; circ 5/5; mixed 1.0).
- 2026-09-24: fold tip-label-protect-expand → tip; LP 43→64/64 · verif 32→42/42; pillars 37/37; circ 5/5; freeze codigo_vivo_tip_label_protect_expand_fold_100pct_20260924_150306
- 2026-09-24: fold tip-pillars-reinforce → tip; pillars 29→37/37; freeze codigo_vivo_tip_pillars_reinforce_fold_100pct_20260924_145946
- 2026-09-24 fold tip-circ-expand → tip: circ 2/2→5/5; BASE 13/13; mixed 1.0; freeze codigo_vivo_tip_circ_expand_fold_100pct_20260924_145451
- 2026-09-24 fold tip-future-track-r3 → tip: track 86.15→99.34 / +dist 95.36→99.52; floors held; freeze `codigo_vivo_tip_future_track_r3_fold_100pct_20260924_144946`.
- 2026-09-24 fold tip-hardneg-r13 → tip @ cab1873; freeze `codigo_vivo_tip_r13_100pct_20260924_144457`; R13 52/52·44/44; mixed 1.0; floors held.
- 2026-09-24 fold tip-distance-far → tip @ `5fb00e3`; freeze `codigo_vivo_tip_distance_far_fold_100pct_20260924_143716`; far MAE 4.653→2.600; DZ/mid/inv/R12 held.
- 2026-09-24 14:31:02 ET: **FOLDED** tip-inverse-r3 → tip; freeze `codigo_vivo_tip_inverse_r3_fold_100pct_20260924_143102`; inv_cv 99.82→100.0; mixed 1.0; collision/choose_safest 100%; mid+R12 floors held. RO adapters.
- 2026-09-24 fold tip-hardneg-r12 → tip; freeze `codigo_vivo_tip_r12_100pct_20260924_142830`; mixed 1.0; R12 52/52·44/44.
- 2026-09-24 14:23:29 ET: **FOLDED** tip-distance-mid → tip; freeze `codigo_vivo_tip_distance_mid_100pct_20260924_142329`; mid/DZ/TTI/R11/motion/collision floors held. RO adapters.
- 2026-09-24 fold tip-tti → tip; freeze `codigo_vivo_tip_tti_fold_100pct_20260924_141146`; TTI 100% scorable; floors held.
- 2026-09-24 14:07:23 ET — fold tip-hardneg-r11 → codigo-vivo-tip; freeze `codigo_vivo_tip_r11_100pct_20260924_140723`; mixed 1.0; R11 52/52·44/44; motion 100%; vision BASE 1.000; circ 2/2; inverse_cv 99.82%; collision 100%.
- 2026-09-24 14:02:26 ET — fold tip-motion-r4 → codigo-vivo-tip; freeze `codigo_vivo_tip_motion_r4_100pct_20260924_135017`; mixed 1.0; motion 100%; vision BASE 1.000; circ 2/2; inverse_cv 99.82%; collision 100%.
- 2026-09-24 13:55:13 ET — fold tip-vision-ground → codigo-vivo-tip; freeze `codigo_vivo_tip_vision_ground_100pct_20260924_134441`; mixed 1.0; vision BASE 1.000; circ 2/2; inverse_cv 99.82%; collision 100%.
- 2026-09-24 13:49:42 ET — fold tip-inverse-r2 → codigo-vivo-tip; freeze `codigo_vivo_tip_inverse_r2_100pct_20260924_134326`; mixed 1.0; inverse_cv 99.82%; collision 100%; R10 52/52·44/44; motion 97.5%.
- 2026-09-24 13:44 ET — tip-vision-ground polish (pre-fold): BASE vis 0.9→**1.0**; circ 2/2; floor 1.0; see fold entry above.
- 2026-09-24 13:46:15 ET — fold tip-hardneg-r10 → codigo-vivo-tip; freeze `codigo_vivo_tip_r10_100pct_20260924_134615`; mixed 1.0; R10 52/52·44/44; motion 97.5%.
# Estado de avance — Agent Lab / quantum-llm-lab

## 2026-09-24 — fold tip-motion-r3 → codigo-vivo-tip
Motion coverage **97.5%**; mixed **1.0**; R9 **52/52·44/44**; freeze `codigo_vivo_tip_motion_r3_100pct_20260924_133333`. See root STATUS + TIP-MOTION-R3.

## 2026-09-24 — fold tip-hardneg-r9 → codigo-vivo-tip
Rebase onto `3d05cbe` → FF `ea2f450`+`0096a6e`. Mixed (d) **1.0**; R9 **52/52·44/44**; R1–R8+LP held; collision_n/motion_r2 retained. Freeze `codigo_vivo_tip_r9_100pct_20260924_133405`. Motion-r3 not folded. See TIP-R9 + SCOREBOARD.

**Repo:** https://github.com/anthony-x507/quantum-llm-lab  
**Actualizado:** 2026-09-24 ~10:57 ET  
**SSOT del plan:** [`PLAN-MAESTRO-PARTE-1.md`](PLAN-MAESTRO-PARTE-1.md)  
**Regla:** solo números de registro limpio (anti-contam). Sin claims de ventaja cuántica.

---

## 2026-09-24 — fold tip-collision-n → codigo-vivo-tip
Rebase `55277d9`/`c79ab1a` onto `763fb8c` → already up to date; FF. CPU unified **1.0** (re-smoke); collision physics **100%** (2850 queries / **40** eval); motion **91%**; R8 52/52·44/44; LP 43/43·32/32; pillars 26/26; smoke 12/12; `wired_to_vlm`; freezes retained incl. motion_r2 + collision_pred + distance_danger + r8 + scaffold_motion. Freeze `codigo_vivo_tip_collision_n_100pct_20260924_132559`. R9 **not** folded. See SCOREBOARD + TIP-COLLISION-N.

## 2026-09-24 — fold tip-motion-r2 → codigo-vivo-tip
Rebase `9649df2`/`c3cd0a4` onto `4fe070e` → `77d161a`+`4d91a9c` FF. CPU unified **1.0** (re-smoke); motion coverage **91%** (132 ind + 50 corr; +47.0 pp vs 44%); R8 52/52·44/44; LP 43/43·32/32; pillars 26/26; smoke 12/12; `wired_to_vlm`; freezes retained incl. r8 + scaffold_motion + distance_danger + collision_pred (`codigo_vivo_tip_collision_pred_100pct_20260924_131846`). Freeze `codigo_vivo_tip_motion_r2_100pct_20260924_131537`. See SCOREBOARD + TIP-MOTION-R2.

## 2026-09-24 — fold tip-collision-pred → codigo-vivo-tip
Rebase `da7a628`/`c52ea34` onto `fd07999` → `3834ebe`+`30194cb` FF. CPU unified **1.0** (re-smoke); collision physics **100%** (555 queries / 8 eval); R8 52/52·44/44; LP 43/43·32/32; motion **44%**; `wired_to_vlm`; freezes retained incl. r8 + scaffold_motion + distance_danger (`codigo_vivo_tip_distance_danger_100pct_20260924_131243`). Freeze `codigo_vivo_tip_collision_pred_100pct_20260924_131846`. Motion-r2 **not** folded. See SCOREBOARD + TIP-COLLISION-PRED.

## 2026-09-24 — fold tip-distance-danger → codigo-vivo-tip
Rebase `110bcbc` onto `e2a950d` → `da55eac` FF. CPU unified **1.0** (re-smoke); DZ 30–70 m **100%** (orig+danger50); ~50 m **100%**; future-pred DZ ~97%/96.6%; tracking DZ **100%**; R8 52/52·44/44; LP 43/43·32/32; motion **44%**; `wired_to_vlm`; freezes retained incl. r8 + scaffold_motion + r7 + post_od2. Freeze `codigo_vivo_tip_distance_danger_100pct_20260924_131243`. Collision-pred **not** folded. See SCOREBOARD + TIP-DISTANCE-DANGER.

## 2026-09-24 — fold tip-hardneg-r8 → codigo-vivo-tip
Rebase `270ce46`/`c964dcc` onto `d892398` → `afd52c9`+`32b0b14` FF. CPU unified **1.0** (re-smoke); R8 52/52·44/44; R7 52/52·44/44; LP 43/43·32/32; R1–R6 held; motion **44%**; `wired_to_vlm`; freezes retained incl. scaffold_motion + r7 + post_od2. Freeze `codigo_vivo_tip_r8_100pct_20260924_130950`. Distance-danger **not** folded. See SCOREBOARD + TIP-R8.

## 2026-09-24 — fold tip-scaffold-motion → codigo-vivo-tip
Rebase `9ddfaed` onto `69655dd` → `7b0c63b` FF. CPU unified **1.0** (re-smoke); motion coverage **44%**; R7 52/52·44/44; LP 43/43·32/32; R1–R6 held; `wired_to_vlm`; freezes retained incl. r7 + post_od2. Freeze `codigo_vivo_tip_scaffold_motion_100pct_20260924_130131`. See SCOREBOARD + TIP-SCAFFOLD-MOTION.

## 2026-09-24 — tip-scaffold-motion (RGB cue honesty)
Branch `frontier/tip-scaffold-motion` from tip `f0fe729` (rebase onto tip post-R7). Multi-hue GT-free motion cue + scaffold→VLM meta; coverage↑; mixed (d) **1.0** held; wired_to_vlm. See `docs/FRONTIER-CODIGO-VIVO-TIP-SCAFFOLD-MOTION.md`.

## 2026-09-24 — fold tip-hardneg-r7 → codigo-vivo-tip
Rebase `bac0ad0`/`76a3eac` onto `f0fe729` → `00fdaaf`+`f586efd` FF. CPU unified **1.0** (re-smoke); R7 52/52·44/44; LP 43/43·32/32; R1–R6 held; freezes retained incl. post_od2 + R6 + label_protect. See SCOREBOARD + TIP-R7.

## 2026-09-24 — R7 tip freeze codigo-vivo-tip @ f586efd
Freeze `codigo_vivo_tip_r7_100pct`. CPU unified **1.0**; R1–R7 18/18·22/22·35/35·40/40·44/44·48/48·52/52; R3–R7/LP verifier 28/28·32/32·36/36·40/40·44/44·32/32; LP 43/43; `ent_never_on_python`. Prior freezes **retained** (platform / mlx_r3 / post_polish / R5 / LP / R6 / post_od2 / polish_r7). Blockers none. See SCOREBOARD.

## 2026-09-24 — POST-OD2 tip freeze @ 15c9a23
Freeze `codigo_vivo_tip_post_od2_100pct_20260924_125301`. CPU unified **1.0**; R1–R6 18/18·22/22·35/35·40/40·44/44·48/48; LP 43/43·32/32; own-delta Py−0.062 Ent+1.0 Vis−0.200 dual-lane 1.0; wired_to_vlm. Prior freezes **retained** (platform / mlx_r3 / post_polish / R5 / LP / R6). Blockers none. See SCOREBOARD.

## 2026-09-24 — fold tip-own-delta-refresh → codigo-vivo-tip
Rebase `9c9b4d3` onto `4291aab` → `1b56131` FF. CPU unified **1.0** (re-smoke); RAW Py−0.062 Ent+1.0 Vis−0.200; dual-lane held; freezes retained incl. r6 + label_protect. See SCOREBOARD + OWN-DELTA-REFRESH.

## 2026-09-24 — fold tip-hardneg-r6 → codigo-vivo-tip
Rebase onto `3b10288` → `f3fcf1e`+`259e4a4` FF. CPU unified **1.0**; R6 48/48·40/40; LP 43/43·32/32; R1–R5 held. Freezes retained. See SCOREBOARD + TIP-R6.

## 2026-09-24 — R6 tip freeze codigo-vivo-tip @ 259e4a4
Freeze `codigo_vivo_tip_r6_100pct`. CPU unified **1.0**; R1–R6 + LP held. Prior freezes retained. See SCOREBOARD.
## 2026-09-24 — tip own-delta refresh @ 3b10288
Branch `frontier/tip-own-delta-refresh`. RAW Py **−0.062** Ent **+1.0** Vis **−0.200**; dual-lane CPU+MLX sample unified **1.0**; `ro_mtime_unchanged`. See OWN-DELTA-REFRESH + SCOREBOARD.

## 2026-09-24 — LABEL-PROTECT tip freeze @ d151432
Freeze `codigo_vivo_tip_label_protect_100pct_20260924_124608`. CPU unified **1.0**; LP 43/43·32/32; R1–R5 18/18·22/22·35/35·40/40·44/44; R3/R4/R5 verifier 28/28·32/32·36/36; wired_to_vlm; mlx largern + ent-sep + own-delta cited. Prior freezes **retained** (platform / mlx_r3 / post_polish / R5 tip / polish_r5 / LP polish). Blockers none. See SCOREBOARD.

## 2026-09-24 — fold tip-label-protect → codigo-vivo-tip
Rebase `2d86650`/`65de0c9` onto `32fed9b` → `751ed03`+`8b0772a` FF. CPU unified **1.0** (re-smoke); label-protect 43/43·32/32; R1–R5 held; R5 tip freeze retained. See SCOREBOARD + TIP-LABEL-PROTECT.

## 2026-09-24 — tip-label-protect (fall/super)
Branch `frontier/tip-label-protect` from tip `6dce7b6` (tip freeze-busy → separate).  
Router pre→post **36/43→43/43**; verifier **32/32**; mixed (d) **1.0** held ≥0.967; R1–R5 held.  
Reinforce: empty `gates=[]` ops + negated `json válido`. Adapters RO. See `docs/FRONTIER-CODIGO-VIVO-TIP-LABEL-PROTECT.md`.

## Tip hardneg R5 (2026-09-24) — FOLDED

Branch `frontier/tip-hardneg-r5` rebased `9a12fbc`→`49d7ccc` onto tip `b1c7091` (post_polish); FF into `frontier/codigo-vivo-tip`. CPU re-smoke unified **1.0**; R1–R5 routers 18/18·22/22·35/35·40/40·44/44; R3/R4/R5 verifier 28/28·32/32·36/36. Anti-contam CLEAN. Freezes retained incl. post_polish. See `docs/FRONTIER-CODIGO-VIVO-TIP-R5.md`.


## Tip own-delta (2026-09-24) — FOLDED

Branch `frontier/tip-own-delta-scoreboard` rebased `2382c90`→`66db30a` onto tip `0a1ef4d` (ent-sep); FF into `frontier/codigo-vivo-tip`. Py Δ −0.062, Ent +1.0, Vis −0.200; tip dual-lane CPU re-smoke unified **1.0**. Anti-contam CLEAN. Freezes retained + post_polish. See `docs/FRONTIER-CODIGO-VIVO-TIP-OWN-DELTA-SCOREBOARD.md`.


## Goal

Qwen **8B** (**LoRA + capas + tools**) **10×** mejor que el modelo de partida (base sin adapter ≈ **0% JSON usable** → techo **100% usable** por dominio).  
Definición y scoreboard: §0 de Plan Maestro Parte 1.

---

## Por dominio (registro)

### Cuántico

| Hecho | Registro |
|-------|----------|
| LoRA congelado RO | `data/lora_adapter/` — mtime **2026-09-24 00:58:09** — **solo lectura** |
| Own-delta base vs LoRA RO | Base label/Jev/compile/energy **0.0**; LoRA RO label **0.9**, Jev/compile/energy **1.0** (n=10, `eval_compare_rebalance` / `docs/HYBRID-ORACLE-RESULTS.md`) |
| Amplitude embedding | ~**83%** label / **100%** energía (n=12) — **no superó** LoRA texto |
| Bucle híbrido | Gold-free: single-shot label **0.333** → after loop **1.000** (n=12, SHA `bd06c02`) |
| Ent-more | Adapter `data/lora_adapter_ent/` presente (train 1140/1140 reportado tip-of-spear 04:55); **eval own-delta ent pendiente** (screen `qlab-after-ent` a las 05:00 aún veía train/GPU ocupada) |
| Staged | `lora_dataset_ent_v2.jsonl` **460** rows; `lora_dataset_ent_v3.jsonl` **520** rows (CPU enrich; v2 intacto para próximo train post-eval) |

### Planificación inversa (F1 pasiva, dominio separado)

| Métrica | k=1 | k=3 | k=5 |
|---------|-----|-----|-----|
| pos_acc (CV, tol±8px) | **1.000** | **1.000** | **1.000** |
| physics_fail | **0** | **0** | **0** |
| signal_acc | **0.500** | **0.000** (floja) | **0.512** |

Fuente: `data/inverse_planning/EVAL_PASSIVE_CV.json` (push `746b70a`). VLM/LoRA inversa **diferido** (GPU). Contam inject-GT → INVALID PASS.

### Visión temporal (calle + 3 semáforos)

| Pieza | Estado |
|-------|--------|
| Set F1 | `data/video_synth/fase1/` — 50 seq × 16 frames, split 40/10 (shipped) |
| Prototype + 3 capas | `examples/video_temporal_prototype.py` — `WorkingMemory`, `RetrievalIndex` (train-only numpy NN), `TrafficPhysicsTool` |
| Smoke CPU capas | **PASS** — hit real `f1_000_oak_ave` (distance 2.0) → `data/video_synth/fase1/SMOKE_THREE_LAYERS.json` |
| LoRA F1 / own-delta / ablación VLM | **En cola** GPU (`qlora-video-f1`) — números VLM **aún no** |

### Distancia (refuerzo temporal, FLOOR-SCALE + DANGER ZONE 30–70 m)

| Banda / slice | baseline `bcbcdc8` | improved (05:12 ET) | Δ |
|---------------|--------------------|---------------------|---|
| ~5 m | 76.33 | 75.76 | −0.57 |
| **~50 m** | **48.69** | **50.56** | **+1.87** |
| ~100 m | 76.74 | 79.28 | +2.54 |
| ~200 m | 56.73 | 60.73 | +4.00 |
| **overall** | **65.29** | **66.94** | **+1.65** |
| **30–70 m danger** | — | **49.72** | +1.03 vs 48.69 |

**danger50 focused set** (88 seq, eval 18): 30–70 m **60.11%** (**+11.42 pp** vs baseline 48.69); ~50 m band 62.15%. Future-pred in zone: tracking-only 60.05 → +dist **61.69** (+1.64 pp). Soft priors car~4.5 m / ped~1.7 m; lights still floor-span. Anti-contam CLEAN (`danger50_20260924_051252.jsonl`). Quantum `data/lora_adapter/` RO mtime **00:58:09**. VLM/LoRA diferido.


### Colisión predictiva (CPU, dominio separado)

| predictor | k=1 | k=3 | k=5 | overall |
|-----------|-----|-----|-----|---------|
| collision_physics (oracle floor) | **100** | **100** | **100** | **100** |
| inverse_cv (ablation) | 94.1 | 86.0 | 75.7 | 85.2 |
| choose_safest | **100** | **100** | **100** | **100** |

Ablación **+14.8 pp** vs inverse_cv. Contam PASS. Audit `data/eval_audit/collision_20260924_050543.jsonl`. VLM diferido (`lora_adapter_collision/`). Docs: `COLLISION-PREDICTIVE-F1.md`.

### Física clásica (pelotas / cohetes)

Set ~220 escenas + scripts adapter `data/lora_adapter_classical/`. **Own-delta BASE vs LoRA pendiente** — screen `qlora-classical` en cola GPU.

---

## Directivas permanentes

1. Ciclo: comparar → testear → reforzar → seguir → mejorar → (analizar) → seguir.  
2. Congelar al **80–100%** como plataforma; pulir o reforzar alrededor — no abandonar.  
3. Anti-contaminación: GT eval nunca en inferencia; leak → descartar + rerun.  
4. Proactividad **sin** que Anthony corrija el brainstorming: Leader trae opciones; Anthony aprueba/rechaza.  
5. Adapter cuántico RO. Sin bancos vs modelos grandes hasta own-delta 8B. Sin claims Q-advantage.

---

## Qué corre ahora (screens Mac-139 ~05:00 ET)

| Screen | Rol |
|--------|-----|
| `qlab-after-ent` | Post-ent: pilares / eval (a 05:00 log: GPU/train aún ocupada → esperando) |
| `qlora-classical` | Espera GPU → smoke + own-delta clásico |
| `qlora-video-f1` | Espera GPU → train F1 + eval-compare + ablate |
| `qlab-ent-v2-wait` | Tras eval: archive → train ent_v2 (460) |
| `qlab-enrich-plan` | Enrich CPU (sin robar GPU) |

`data/lora_adapter/` RO — mtime 00:58 intacto.

---

## Qué sigue (orden)

1. Cerrar **own-delta** de `lora_adapter_ent/` (limpio).  
2. Si gate OK → train **ent_v2** (460); v3 (520) staged.  
3. Classical own-delta → freeze ≥80% si aplica.  
4. Video F1 LoRA + own-delta + ablación 3 capas.  
5. Reforzar señal inversa @k=3 y distancia (banda ~50 m / estimador) antes de apilar LoRA flojo.  
5b. Collision CPU floor shipped — VLM own-delta when GPU free (`lora_adapter_collision/`).  
6. Actualizar scoreboard 10× en Plan Maestro al caer números VLM.

---


### Visión (MLX grounding)

| Hecho | Registro |
|-------|----------|
| mlx_vlm API kwargs | `62843ad` — `generate(…, image=)` PASS |
| Anti-think JSON parse | **3/3** (was 0/3 @768) — `max_tokens=1536` + strip think + JSON cue + phase-2; evidence `data/frontier_vision_mlx_anti_think_mac111.json` |
| Doc | [`FRONTIER-VISION-MLX-ANTI-THINK.md`](FRONTIER-VISION-MLX-ANTI-THINK.md) |

## Links útiles

- Plan: [`docs/PLAN-MAESTRO-PARTE-1.md`](PLAN-MAESTRO-PARTE-1.md)  
- Hybrid results: [`docs/HYBRID-ORACLE-RESULTS.md`](HYBRID-ORACLE-RESULTS.md)  
- Inverse F1: [`docs/INVERSE-PLANNING-F1.md`](INVERSE-PLANNING-F1.md)  
- Distance F1: [`docs/DISTANCE-EST-F1.md`](DISTANCE-EST-F1.md)  
- Three layers: [`docs/THREE-LAYERS-PROTOTYPE.md`](THREE-LAYERS-PROTOTYPE.md)

*Fin estado — regenerar al cerrar cada cara larga.*
