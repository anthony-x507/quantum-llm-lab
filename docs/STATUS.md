# Estado de avance — Agent Lab / quantum-llm-lab

**Repo:** https://github.com/anthony-x507/quantum-llm-lab  
**Actualizado:** 2026-09-24 ~05:00 ET  
**SSOT del plan:** [`PLAN-MAESTRO-PARTE-1.md`](PLAN-MAESTRO-PARTE-1.md)  
**Regla:** solo números de registro limpio (anti-contam). Sin claims de ventaja cuántica.

---

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

### Distancia (refuerzo temporal, FLOOR-SCALE)

| Banda | % correct (heurística CPU) |
|-------|----------------------------|
| ~5 m | 76.33 |
| ~50 m | 48.69 |
| ~100 m | 76.74 |
| ~200 m | 56.73 |
| **overall** | **65.29** |

Ablación future-pred: tracking-only **73.51%** > +floor-dist **64.24%** (honesto; estimador ruidoso). Fuente: `EVAL_FLOOR_SCALE_CPU.json` (`bcbcdc8`). VLM/LoRA distancia diferido. Escala = **pisos de edificio** 2.4–3.0 m — **no** alturas fijas de semáforo.

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
6. Actualizar scoreboard 10× en Plan Maestro al caer números VLM.

---

## Links útiles

- Plan: [`docs/PLAN-MAESTRO-PARTE-1.md`](PLAN-MAESTRO-PARTE-1.md)  
- Hybrid results: [`docs/HYBRID-ORACLE-RESULTS.md`](HYBRID-ORACLE-RESULTS.md)  
- Inverse F1: [`docs/INVERSE-PLANNING-F1.md`](INVERSE-PLANNING-F1.md)  
- Distance F1: [`docs/DISTANCE-EST-F1.md`](DISTANCE-EST-F1.md)  
- Three layers: [`docs/THREE-LAYERS-PROTOTYPE.md`](THREE-LAYERS-PROTOTYPE.md)

*Fin estado — regenerar al cerrar cada cara larga.*
