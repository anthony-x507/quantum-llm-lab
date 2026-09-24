> **SSOT 2026-09-24:** el plan vivo es [`PLAN-MAESTRO-PARTE-1.md`](PLAN-MAESTRO-PARTE-1.md). Este archivo conserva el mapa histórico de fases 0–5.

# Plan maestro — Agent Lab (visión cuántica + LoRA + QEC)

Roadmap único para `anthony-x507/Agent-Lab-` (y espejo `quantum-llm-lab`). Todo **local** (M4 128 GB / Studio 36 GB). Sin Cloud Agents para este carril.

Última refine: 2026-09-23 ~21:07 ET.

---

## Mapa de fases

| Fase | Nombre | Estado | Entregable |
|------|--------|--------|------------|
| **0** | Clúster + tooling | Hecho (docs/scripts en main) | README clúster M4=8B / Studio=2B–4B; bridge, Jev, visión |
| **1** | Dataset sintético mixto | Scripts listos; generar en M4 | `data/scenes/` ≥280: caídas + figuras nuevas + entrelazamiento + superposición |
| **2** | LoRA joint (Qwen3-VL-8B) | Plan+scripts listos; **espera modelo+dataset** | `data/lora_adapter/` + eval +20 pts Jev / labels |
| **3** | QEC robustez | **En main** (`3d4ea99`) | `docs/quantum_error_correction.md` + `qec_robustness.py --self-test` PASS |
| **4** | Cableado vivo 8B↔QEC | Pendiente post-smoke | Hooks MLX / reinject system tras síndrome |
| **5** | Eval continuo + log | En curso (descarga 8B) | `data/experiment_log.jsonl` + ciclo 5→N escenas |

Detalle LoRA: [`lora_plan.md`](lora_plan.md). Detalle QEC: [`quantum_error_correction.md`](quantum_error_correction.md).

---

## Fase 0 — Hecho

- Repo: https://github.com/anthony-x507/Agent-Lab-
- Scripts: `llm_quantum_bridge`, `vision_grounding`, `jev_arbiter`, `synthetic_physics_dataset`, `train_lora`, `eval_lora`, `qec_robustness`
- Hardware: M4 = `Qwen3-VL-8B-Thinking-4bit`; Studio = 2B/4B Thinking (Studio offline ~20d — HOLD)

---

## Fase 1 — Dataset (refine)

Generar **una sola mezcla** (no packs separados):

```bash
python examples/synthetic_physics_dataset.py --n-scenes 280 --out data/scenes --seed 42
```

Cuotas objetivo: ~55% fall / ~22% entanglement / ~23% superposition.  
Figuras: square… + **pentagon, hexagon, star, ring** + multi+viento.  
Labels: `fall`, `fall_multi`, `entangled`, `separable`, `superposed`, `collapsed`.

**Criterio de cierre Fase 1:** `SUMMARY.json` con los 3 dominios presentes y ≥200 escenas.

---

## Fase 2 — LoRA joint (refine)

Un **solo** adapter sobre todo el mix (no LoRAs por dominio).

```bash
python examples/train_lora.py --rank 32 --alpha 32 --lr 2e-4 --epochs 3
python examples/eval_lora.py --adapter data/lora_adapter --n-test 10
```

Hipers: rank 16–64, alpha 32, lr 2e-4, 3–5 epochs, ~2–3 h M4.  
Éxito: +20 pts Jev APROBAR **o** acierto de label de dominio ≥7/10.

**Bloqueantes hoy:** (1) pesos 8B cacheados en M4, (2) `data/scenes/` generado.

---

## Fase 3 — QEC (cerrada en repo)

Commit tip con QEC: ver `git log -1 --grep=qec`.  
Self-test: `python examples/qec_robustness.py --self-test`.  
Analogía: prompt adversarial = error Pauli; síndrome → reset a estado coherente.

No bloquea el train LoRA; se desarrolla en paralelo y se cablea en Fase 4.

---

## Fase 4 — Cableado vivo (siguiente refine técnico)

1. Exportar firma de activaciones / embedding de prompt del 8B (MLX).  
2. Proyectar a rejilla 3×3 del guard.  
3. Si síndrome ≠ 0 → reinyectar system + tarea limpia **antes** de `generate`.  
4. Loguear en `experiment_log.jsonl`: `qec_detected`, `qec_corrected`.

---

## Fase 5 — Experimento en vivo (GPS ahora)

1. ~~Setup venv mlx-vlm + PennyLane en M4~~ (en curso / hecho por executor).  
2. **Descargar** `mlx-community/Qwen3-VL-8B-Thinking-4bit` (en curso; HF sin token = lento).  
3. Smoke español una frase.  
4. Ciclo 5 escenas + Jev → `data/experiment_log.jsonl`.  
5. Empujar log a Agent-Lab- cuando haya ≥5 filas.  
6. Ampliar a N=50 cuando 8B estable.  
7. Solo entonces: generar 280 escenas + `train_lora.py`.

---

## Dependencias / HOLD

| Item | Estado |
|------|--------|
| Cursor Cloud Agents | **NO** (crédito lock) — solo Grok Bot + `gh` |
| HF_TOKEN | Ideal para acelerar; si falta, seguir sin auth |
| Mac Studio Tailscale | Offline — HOLD 2B/4B allí |
| Desk F7 DMG quota | HOLD (otro carril) |

---

## Criterio “plan maestro listo para ejecutar”

- [x] Docs LoRA + QEC + este GPS en main  
- [x] Scripts train/eval/dataset/qec en main  
- [ ] 8B cargado + smoke OK en M4  
- [ ] experiment_log ≥5 con Jev  
- [ ] Dataset 280 mixto en disco M4  
- [ ] Primer train LoRA (o dry `--prepare-only` verificado)

Cuando Anthony vuelva: una línea de estado = última casilla abierta arriba.
