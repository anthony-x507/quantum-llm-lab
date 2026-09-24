# Plan de fine-tune con LoRA (Agent Lab / M4)

Documento listo para ejecutar cuando existan: (1) dataset sintético mixto en `data/scenes/` (~200+ escenas) y (2) pesos locales de `mlx-community/Qwen3-VL-8B-Thinking-4bit`.

## Qué es LoRA

**LoRA** (Low-Rank Adaptation) congela los pesos del modelo base e inserta matrices pequeñas entrenables (rango bajo) en capas elegidas — aquí, sobre todo las lineales del **language model** (atención / MLP). Solo se actualizan esos adaptadores; el archivo resultante pesa megabytes, no gigabytes.

En este lab usamos **mlx-vlm** (`python -m mlx_vlm.lora` o los wrappers `examples/train_lora.py` / `eval_lora.py`). Qwen3-VL es un modelo de visión+texto: `mlx-lm` solo no alcanza; el camino canónico es mlx-vlm (que a su vez usa el backend MLX).

## Por qué sirve aquí

Queremos que el 8B, con **un solo adapter** entrenado en **todos los dominios juntos**, proponga más a menudo circuitos JSON que:

1. **Compilen** en PennyLane (puertas h/x/y/z/cx/ry).
2. Respeten la **pérdida de energía** en escenas de caída.
3. Distingan **entrelazamiento** vs estado separable y propongan Bell (H+CX) o producto.
4. **Sostengan superposición** (no colapsar prematuramente) cuando la escena aún muestra hipótesis A|B.
5. Pasen el árbitro **Jev** (APROBAR) en el dominio de caídas.

Sin reentrenar los ~8B parámetros enteros: en la M4 128 GB cabe QLoRA 4-bit + rank 16–64 con batch pequeño.

## Datos (mixto: un solo JSONL)

Fuente: `examples/synthetic_physics_dataset.py` → `data/scenes/`.

`train_lora.py` mezcla **todo** en `data/lora_dataset.jsonl` con campos `domain` + `label` por fila.

### Dominio A — Caídas / figuras visuales

- PNG(s) de frames (formas que caen, rebotan, viento, multi-objeto).
- `meta.json` con verdad física: forma, color, gravedad efectiva, restitución, rebotes, pérdida de energía, trayectoria.
- **Figuras ampliadas:** square, circle, triangle, rectangle, irregular_polygon, **pentagon, hexagon, star, ring**, más combinaciones (ej. cuadrado rojo + círculo azul con `lateral_wind`).

Target toy: H + CX + RY(θ) según pérdida por rebote. Labels: `fall` / `fall_multi`.

### Dominio B — Entrelazamiento cuántico

Subconjunto (~22% de escenas) con metáfora visual de **dos partículas**:

| Label | Visual | Circuito target |
|-------|--------|-----------------|
| `entangled` | Enlace + trayectorias anti-correlacionadas; tag violeta; `bell_state` ∈ {Φ±, Ψ±} | `[["h",0],["cx",0,1]]` |
| `separable` | Sin enlace; trayectorias independientes | `[["h",0],["h",1]]` (producto) |

El 8B debe **reconocer** si la descripción visual es sistema entrelazado vs separable y **proponer** el circuito acorde (Bell vs producto).

### Dominio C — Superposición

Subconjunto (~23%) con metáfora de **dos hipótesis fantasma** A|B:

| Label | Visual | Circuito target |
|-------|--------|-----------------|
| `superposed` | Ambas formas semitransparentes + arco “brace”; sin flash de medida | `[["h",0]]` — sostener A\|B |
| `collapsed` | Tras `measure_frame`, una sola forma + flash | H (+ X si colapsó a B) |

El LoRA entrena la capacidad de **no colapsar prematuramente** cuando la escena sigue en superposición.

### Tamaño mínimo

**≥200 escenas** mezcladas (caídas + entrelazamiento + superposición). El generador reparte ~55% / ~22% / ~23%. Opcional: enriquecer targets de caída con filas `APROBAR` de `data/experiment_log.jsonl`.

## Hiperparámetros (punto de partida M4)

| Parámetro | Valor sugerido | Notas |
|-----------|----------------|-------|
| Modelo | `mlx-community/Qwen3-VL-8B-Thinking-4bit` | Ya en el clúster M4 |
| LoRA rank | **16–64** (default script: **32**) | Subir si underfitting |
| LoRA alpha | **32** (o ~2× rank) | Escala del update |
| Learning rate | **2e-4** | Típico QLoRA VLM |
| Epochs | **3–5** | Vigilancia de val loss |
| Batch size | 1–2 | + grad accumulation 4–8 |
| Max seq | 2048 | Escenas con 1 frame |
| train-vision | off al inicio | Encender si falla el ground visual |
| Dropout LoRA | 0.0–0.05 | |
| Muestreo | **joint** | Un solo adapter; no entrenar dominios por separado |

Tiempo estimado en **M4 128 GB**: **~2–3 horas** para ~200–280 escenas × 3–5 epochs (QLoRA). Con ~400 (más figuras + quantum), planear ~3–5 h.

## Criterios de éxito

Hold-out de **10 escenas** estratificadas si es posible (caída + entrelazado + superposición) vía `examples/eval_lora.py`:

| Métrica | Éxito mínimo post-LoRA |
|---------|-------------------------|
| JSON parseable | ≥ 8/10 |
| Compila PennyLane | ≥ 8/10 |
| Jev APROBAR (subconjunto fall) | ≥ 7/10 del subset fall |
| Label domain correcto (entangled/separable/superposed/collapsed) | ≥ 7/10 en subset quantum |
| Delta vs base | **+20 puntos** en tasa Jev APROBAR **o** en acierto de label de dominio |

## Secuencia de ejecución

```bash
# 1) Dataset mixto (caídas + entrelazamiento + superposición + figuras nuevas)
python examples/synthetic_physics_dataset.py --n-scenes 280 --out data/scenes --seed 42

# 2) (Opcional) ciclo Jev para enriquecer targets de caída
python examples/run_jev_experiment.py --n 5

# 3) Train (TODO junto)
python examples/train_lora.py \
  --model mlx-community/Qwen3-VL-8B-Thinking-4bit \
  --scenes data/scenes \
  --out data/lora_adapter \
  --rank 32 --alpha 32 --lr 2e-4 --epochs 3

# 4) Eval
python examples/eval_lora.py \
  --model mlx-community/Qwen3-VL-8B-Thinking-4bit \
  --adapter data/lora_adapter \
  --scenes data/scenes --n-test 10
```

## Cargar el adapter después

```python
from mlx_vlm import load, generate
model, processor = load(
    "mlx-community/Qwen3-VL-8B-Thinking-4bit",
    adapter_path="data/lora_adapter",
)
```

O CLI: `python -m mlx_vlm.generate --model ... --adapter-path data/lora_adapter ...`



## Fase 3: Corrección de errores cuánticos (después del LoRA básico)

**Siguiente paso** cuando el LoRA joint (caídas + entrelazamiento + superposición) ya esté entrenado y evaluado.

Documento: [`docs/quantum_error_correction.md`](quantum_error_correction.md).  
Demo + tests: `python examples/qec_robustness.py --self-test`.

### Qué aporta

Capa **experimental** de robustez: inspirada en código de superficie / Shor. Trata un prompt adversarial como “error Pauli” sobre una rejilla 3×3 de representaciones internas; el **síndrome** detecta drift y el decoder **revierte** al estado coherente **antes** de generar la respuesta.

### Dependencias

- **PennyLane** ≥ 0.38 (ya en `requirements.txt` del lab).
- LoRA Fase 1–2 opcional para la demo del código (la simulación QEC corre sola).
- Cablear activaciones reales del 8B (MLX hooks) = sub-fase 3.b; la demo actual usa embedding toy del texto.

### Criterios de éxito (Fase 3)

| Criterio | Meta |
|----------|------|
| Self-test | `qec_robustness.py --self-test` exit 0 |
| Prompt limpio | Síndrome trivial; respuesta coherente |
| Prompt adversarial | Síndrome ≠ 0; tras corrección, respuesta = baseline coherente (no filtrada/jailbreak) |
| PennyLane | Circuito 3×3 detecta X inyectado en qubit de datos |

No bloquea el train LoRA: se puede desarrollar en paralelo, pero se **posiciona** como Fase 3 en el roadmap del adapter.

## Fuera de alcance (por ahora)

- Fine-tune completo de pesos.
- Entrenar en la Studio (36 GB): usar 2B/4B Thinking allí, no el 8B.
- Adapters separados por dominio (el diseño actual es **un** LoRA joint).
- Subir adapters a la nube: todo local / este repo.
