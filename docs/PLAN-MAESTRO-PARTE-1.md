# Plan Maestro — Parte 1

**Repo:** `anthony-x507/quantum-llm-lab`  
**Hardware:** Mac M4 (`Qwen3-VL-8B-Thinking-4bit`)  
**Estado:** fuente única de verdad (SSOT) — **iterar y mejorar**, no archivar  
**Creado:** 2026-09-24 ~04:51 ET · **GOAL 10×:** 2026-09-24 ~04:55 ET · **§5.1 proactividad + freeze 80–100%:** 2026-09-24 ~04:57 ET  
**Supersede parcial:** `docs/PLAN-MAESTRO.md` (fases 0–5 históricas) queda como archivo de fases tempranas; **este documento manda** para visión, dominios, capas y ciclo.

---

## 0. GOAL — 10× sobre el modelo de partida

**Meta de Anthony (2026-09-24 ~04:55 ET):** un Qwen 8B que supere **diez veces (10×)** al modelo de partida — el **base sin adapter**, que daba **~0% JSON usable**.

### Definición medible de 10×

El base parte en **~0% usable**. En ese régimen, **10× = 100% usable** en **todos** los dominios (cuántico, física clásica, visión temporal, planificación inversa, distancia), con label / energía / tracking en el **techo** del dominio.

Si no cabe un solo cociente “10×” en una métrica (porque el base es 0 → cociente infinito), se **desglosa**:

| Eje 10× | Qué mide | Techo |
|---------|----------|-------|
| Parseo usable | JSON/estructurado válido post-parse (sin basura Thinking) | 100% |
| Label correcto | Etiqueta / clase / decisión de dominio correcta | 100% |
| Tracking temporal | Objetos seguidos + resumen coherente (F1 calle) | ~≥80% gate apilar; techo 100% |
| Predicción inversa | Posición ±tol @ k=1,3,5 + señal + physics-law | 100% pos; señal→100%; physics_fail→0 |
| Distancia | % metros correctos por banda (tol 10%/20%) | 100% |

**Compuesto:** el producto / promedio de ejes del dominio debe ser **≥10×** sobre el base del mismo eje (si base=0%, el techo 100% **cuenta como 10× cumplido** en ese eje).  
No se declara dominio “10× cerrado” hasta tener **own-delta limpio** (base VLM vs trained) en ese dominio — no CV/heurística sola, salvo nota explícita.

**Prohibido:** claims de ventaja cuántica; bancos contra modelos grandes; GT de eval en inferencia.

---

## 0.1 Scoreboard 10× (actualizar al salir números)

> Solo números de evals **limpias** (anti-contam). `PEND` = falta own-delta VLM. Heurística/CV no cierra el goal 10× del 8B.

| Dominio | Métrica clave | Baseline (base VLM, sin adapter) | Actual | Target 10× | Gap | Siguiente acción (capa) |
|---------|---------------|----------------------------------|--------|------------|-----|-------------------------|
| **Cuántico** — parseo usable | JSON/Jev válido | **0.0** (n=10, `eval_compare_rebalance`) | **1.0** Jev / compile (LoRA RO) | 1.0 | **0** en Jev/compile | Mantener RO; enriquecer con `lora_adapter_ent/` + ent_v2 |
| **Cuántico** — label | label_acc | **0.0** | **0.9** LoRA RO; loop híbrido **1.0** (n=12, gold-free) | 1.0 | **0.1** vs LoRA; **0** vs loop | Apilar tools/oráculo + QEC; amplitude embed **no** apilar (perdió vs LoRA texto) |
| **Cuántico** — energía | energy_ok | **0.0** | **1.0** LoRA RO / loop | 1.0 | **0** | Congelar práctica; no claim Q-advantage |
| **Física clásica** | label / física visual | **PEND** (BASE VLM) | set 220 escenas; gold CPU 1.0 ≠ VLM | 1.0 | **PEND** | Smoke + own-delta BASE vs `lora_adapter_classical/` (GPU cola) |
| **Visión temporal F1** | tracking + resumen | **PEND** | set 50×16 shipped; LoRA en cola | ≥0.80 gate / 1.0 techo | **PEND** | Train `lora_adapter_video_f1/` → own-delta → ablación 3 capas |
| **Planif. inversa F1** | pos @k=1,3,5 | **PEND** (VLM) | CV: pos **1.0**; señal 0.50/0.00/0.51 | 1.0 pos+señal | Señal **débil** (CV); VLM **PEND** | Reforzar señal; LoRA `lora_adapter_inverse/` tras GPU; cruzar “anticipar error” con cuántico |
| **Distancia** | % correct@tol por banda | **PEND** (VLM) | Heurística piso: **65.3%** overall (5m 76% / 50m 49% / 100m 77% / 200m 57%) | 1.0 | ~**35 pp** overall (heurística); VLM **PEND** | Diagnosticar banda ~50m; **no** apilar LoRA hasta estimar si VLM supera heurística; ablación: +dist **empeoró** future-pred (73.5→64.2) — reforzar estimador antes de creer el refuerzo |
| **Compuesto lab** | ejes ≥10× / techo | base ~0 usable | cuántico cerca del techo en parse/label/energía; resto PEND | todos dominios en techo | **grande** fuera de cuántico | Ciclo permanente; GPU: ent → classical → video F1 → distance/inverse |

### Capas que cierran cada tipo de gap

| Gap típico | Capas candidatas (orden train-first) |
|------------|--------------------------------------|
| Parseo / JSON basura | LoRA dominio + anti-think parse; **no** más prompt theater |
| Label / energía cuántica | LoRA (`lora_adapter` RO ya); ent_v2; hybrid oracle/tools; QEC; amplitude embed solo si supera LoRA texto |
| Tracking temporal | LoRA video F1; memoria trabajo; retrieval train-only; tools sim |
| Predicción inversa | LoRA inverse; memoria; tools física; cruzar con cuántico “anticipar error” |
| Distancia | Floor-scale + parallax; luego LoRA `lora_adapter_distance/` **si** own-delta ≥ gate; Jeff **después** de tracking básico |
| Seguridad / grants | **Jeff** (separado; post-tracking) |

**Última actualización scoreboard:** 2026-09-24 ~04:55 ET · tip `bcbcdc8` + Parte 1.

---
## 1. Visión

Goal medible: **§0 — 10×** sobre el base (~0% JSON usable). Enseñar a **Qwen 8B** (LoRA + herramientas + memoria/retrieval) a ser más inteligente en:

- física **cuántica** (circuitos, entrelazamiento, oráculo híbrido, QEC),
- **visión temporal** (calle, semáforos, tracking, resumen),
- **planificación inversa** (predecir el futuro bajo acción hipotética),
- **distancia** (metros reales vía referencia de pisos + parallax).

Competir en **herramientas y método**, no en tamaño de modelo.  
Sin claims de “ventaja cuántica”. Sin bankear contra Gemini/GPT/SOTA grandes hasta tener **delta propio** del 8B entrenado vs el mismo 8B sin entrenar en ese dominio.

---

## 2. Dominios (en paralelo)

### 2.a Cuántico

| Pieza | Nota |
|-------|------|
| Escenas | Entrelazamiento / superposición / caída (dataset mixto) |
| LoRA | Adapter congelado `data/lora_adapter/` (~333 MB) — **SOLO LECTURA** |
| Amplitude embedding | Pieza 1: ~83% label / 100% energía (n=12); **no superó** LoRA texto — resultado honesto |
| Bucle híbrido | Modelo → oráculo (gold-free own-delta hecho) |
| QEC | Steane / códigos de superficie (real, no teatro) |
| Tensor networks | MPS (roadmap; no bloquear tip-of-spear) |
| En curso | `qlora-ent` → `data/lora_adapter_ent/`; staged ent_v2 (460 rows) |

Nuevos adapters cuánticos van a **dirs nuevos** (`lora_adapter_ent/`, …). Nunca sobrescribir ni fusionar el congelado.

### 2.b Física clásica (visual)

Pelotas (béisbol / soccer / golf: spin, choques, impulso), cohetes, colisiones.  
Adapter propio: `data/lora_adapter_classical/`. Own-delta = BASE vs classical LoRA **solo** (sin bancos externos).

### 2.c Visión temporal (calle)

Una calle, **3 semáforos**, intersecciones ruidosas, peatones, carros, nombres de calle.

| Fase | Alcance |
|------|---------|
| **1** | 3 semáforos + tracking + resumen estructurado |
| **2** | Giros |
| **3** | Múltiples calles |

Set F1: `data/video_synth/fase1/` (50×16, split 40/10). Prototype: `examples/video_temporal_prototype.py` (capas + anti-contam + ablación). Adapter: `data/lora_adapter_video_f1/` (cola GPU). Gate ~≥80% own-delta antes de LoRA F2.

### 2.d Planificación inversa (dominio **separado**)

Modelo en frame N predice frame N+k bajo acción hipotética; GT = realidad N+k (**nunca** visible en inferencia).

| Fase | Modo |
|------|------|
| **1** | Pasiva (predicción sin elegir acción) — CV baseline shipped (`746b70a`) |
| **2** | Condicional a acción |
| **3** | Elige acción óptima (planning) |

Métricas F1: % posición correcta ±tol por horizonte k=1,3,5; physics-law fail si trayectoria imposible.  
Adapter futuro: `data/lora_adapter_inverse/` **solo**. No mezclar adapters/GT con calle ni cuántico.  
Cuando haya números de “anticipar el error” en ambos mundos → **cruzar** con dominio cuántico (lógica, no adapters compartidos).

### 2.e Distancia (refuerzo de visión temporal)

- **Referencia de escala = pisos del edificio:** cada piso ≈ 8–10 pies (2.4–3.0 m). **NO** alturas fijas de semáforos (varían ~3–5 m).
- Derivar altura aparente del semáforo/señal por cuántos pisos ocupa en el frame → triangulación a **carros, intersecciones, stop signs, peatones** (y al semáforo).
- Señales: **parallax** entre frames (crece → se acerca; encoge → se aleja) + referencia de pisos.
- Set ≥50 secuencias con GT de metros (render sintético con posición conocida).
- Salida modelo: objeto + distancia estimada + confianza.
- Tolerancia: **10%** si GT &lt; 50 m; **20%** si 50–200 m.
- Métrica clave: % correcta por rango **y** si la distancia mejora tracking y predicción inversa vs tracking solo.
- Anti-contam: distancias GT **nunca** en inferencia.

---

## 3. Capacidades transversales (paralelo, entrelazadas)

Interlock: **memoria → retrieval → tool → memoria**.

| Capa | Regla |
|------|--------|
| **Memoria de trabajo** | Buffer de objetos/predicciones/estado percibidos por el modelo — **nunca** GT/labels |
| **Retrieval** | Índice = **solo train**; cero ejemplos de eval; leak = inválido → descartar + rerun limpio |
| **Tool use** | PennyLane / NumPy / sims reales — no inventar números ni devolver answer keys |
| **Jeff** | Reglas de seguridad **separadas**; se apilan **después** de tracking básico sólido |

Detalle: `docs/LOCK-THREE-LAYERS.md`, `docs/LOCK-ANTI-CONTAMINATION.md`. Prototype vive en video F1 (no forks competidores).

---

## 4. Ciclo permanente de trabajo

```
comparar → testear → reforzar → seguir → mejorar
    → (si hace falta) parar y analizar qué funciona / qué no
    → seguir
```

- Aplica a **todos** los dominios en paralelo.
- **NUNCA** pausar por éxito (“ya está bien”) ni abandonar por tropiezo.
- Si una métrica sube → apilar la siguiente capa de refuerzo alrededor.
- Si cae → diagnosticar, corregir, empujar la aguja otra vez.

Locks: `docs/LOCK-WORK-CYCLE.md`, `docs/LOCK-CONTINUOUS-SELF-IMPROVE.md`, `docs/LOCK-TRAIN-FIRST-OWN-DELTA.md`.

---

## 5. Restricciones duras (no negociables)

1. **Anti-contaminación** — GT de eval nunca en prompt, memoria de trabajo ni retrieval en inferencia. Comparación solo post-hoc. Si se contamina: **descartar run + repetir limpio**. Auditar qué tocó el modelo en cada eval.
2. **Train-first / own-delta** — entrenar 8B+LoRA en el dominio → medir salto vs **mismo** modelo sin entrenar. Apilar siguiente capa solo si el salto es sustancial (~**≥80%** tracking+resumen coherente o equivalente de dominio). Si no, diagnosticar antes de apilar.
3. **Sin bancos contra modelos grandes** hasta tener ese delta propio del 8B.
4. **Adapter cuántico** `data/lora_adapter/` — **solo lectura**.
5. **Sin claims de ventaja cuántica.**
6. **Proactividad del Leader** — ver **§5.1.A**: Leader trae ángulos (incl. los que contradicen); dos respuestas (refuerza/cuestiona); Anthony solo aprueba/rechaza — **no** corrige el brainstorming.
7. **Congelar 80–100%** — ver **§5.1.B**: avance sustancial se congela como plataforma; pulir o reforzar alrededor; nunca abandonar un 80%.
7. Cola GPU compartida (`data/TRAIN_LOCK.txt`); no matar screens ajenos; adapters por dominio en dirs separados.

---

## 5.1 Directivas permanentes (2026-09-24 ~04:57 ET)

### A) Proactividad sin corrección (brainstorming = Leader)

- **ABACO LEADER** genera **múltiples ángulos** de mejora por su cuenta en cada tropiezo o avance.
- Anthony **no** tiene que corregir ni sugerir el brainstorming.
- Si una idea del Leader es mala, el Leader la **descarta** y trae la siguiente.
- Anthony solo **aprueba o rechaza** opciones ya formuladas — no lidera el ideario.
- Compatibilidad: la regla de “dos respuestas por idea (refuerza / cuestiona)” sigue; ambas las escribe el Leader.

### B) Congelar al 80–100% (plataforma, no abandono)

Cuando un dominio o métrica llega a **~80%, ~90% o 100%** (avance sustancial medido en eval limpia):

1. Se **CONGELA** ese resultado como **baseline de plataforma** (artifact + número + SHA/audit).
2. Luego, en paralelo o secuencia:
   - **(a)** pulir para subir el número hacia el techo 10×, y/o
   - **(b)** trabajar **alrededor**: reforzar otras reglas/capas para que el sistema quede más **unido y uniforme**.
3. **No se abandona** un 80% — se aprovecha como base de apilado.
4. Aplica a **todos** los dominios: cuántico, física clásica, visión temporal, planificación inversa, distancia.

Congelados de ejemplo (actualizar al cerrar caras):

| Dominio / eje | % congelado | Nota |
|---------------|-------------|------|
| Cuántico Jev/compile (LoRA RO) | ~100% | Plataforma RO; no overwrite `data/lora_adapter/` |
| Cuántico label (LoRA RO) | ~90% | Pulir con ent / loop; no bajar el piso |
| Cuántico label (hybrid loop n=12) | 100% | Plataforma tools; gold-free |
| Inversa pos CV @k | 100% | CV ≠ VLM; congelar como ref heurística; VLM propio pendiente |
| Distancia heurística overall | ~65% | **Aún no** congela plataforma 80% — diagnosticar antes |

---
## 6. Cola tip-of-spear (vivo — actualizar al cerrar caras)

Orden típico GPU (revisar screens reales):

1. `qlora-ent` (running / closing)
2. `qlab-after-ent` (pilares + own-delta ent)
3. `qlora-classical`
4. `qlora-video-f1` (train → eval-compare → ablate)
5. `qlab-ent-v2-wait`
6. Distancia (CPU set primero; LoRA `data/lora_adapter_distance/` solo si gate y GPU libre)
7. Inverse LoRA cuando F1 CV + gate lo pidan

CPU puede avanzar sets, evals heurísticos, docs y anti-contam audits en paralelo.

---

## 7. Cómo evoluciona este documento

- Es **Parte 1**: visión + mapa. Partes siguientes (métricas tablas, calendarios, resultados por cara) se **añaden** o se editán aquí — no proliferar planes paralelos.
- Cada LOCK de voz nuevo se refleja en §2–§5 el mismo día.
- Números solo de evals limpios auditados; nunca inventar ni pegar peeks pretrain como gate.

---

## 8. Índice de locks relacionados

| Doc | Tema |
|-----|------|
| `LOCK-TRAIN-FIRST-OWN-DELTA.md` | Train → medir propio delta; umbral ~80% |
| `LOCK-CONTINUOUS-SELF-IMPROVE.md` | Nunca pausar por éxito/tropiezo |
| `LOCK-WORK-CYCLE.md` | Ciclo comparar→…→seguir |
| `LOCK-THREE-LAYERS.md` | Memoria / retrieval / tools |
| `LOCK-ANTI-CONTAMINATION.md` | GT nunca en inferencia |
| `LOCK-INVERSE-PLANNING.md` | Dominio inverso separado |
| `INVERSE-PLANNING-F1.md` | Números F1 pasiva |
| `THREE-LAYERS-PROTOTYPE.md` | Pointer a video F1 |

---

*Fin Parte 1 — iterar aquí.*
