# Plan Maestro — Parte 1

**Repo:** `anthony-x507/quantum-llm-lab`  
**Hardware:** Mac M4 (`Qwen3-VL-8B-Thinking-4bit`)  
**Estado:** fuente única de verdad (SSOT) — **iterar y mejorar**, no archivar  
**Creado:** 2026-09-24 ~04:51 ET (voz Anthony → ABACO LEADER)  
**Supersede parcial:** `docs/PLAN-MAESTRO.md` (fases 0–5 históricas) queda como archivo de fases tempranas; **este documento manda** para visión, dominios, capas y ciclo.

---

## 1. Visión

Enseñar a **Qwen 8B** (LoRA + herramientas + memoria/retrieval) a ser más inteligente en:

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
6. **Proactividad del Leader** — proponer ideas (incluidas las que **contradicen** a Anthony). Por cada idea material: **dos respuestas** — una que **refuerza** y una que **cuestiona**. Anthony decide.
7. Cola GPU compartida (`data/TRAIN_LOCK.txt`); no matar screens ajenos; adapters por dominio en dirs separados.

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
