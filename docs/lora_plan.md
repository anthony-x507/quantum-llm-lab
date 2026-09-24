# Plan de fine-tune con LoRA (Agent Lab / M4)

Documento listo para ejecutar cuando existan: (1) dataset sintético en `data/scenes/` (~200+ escenas) y (2) pesos locales de `mlx-community/Qwen3-VL-8B-Thinking-4bit`.

## Qué es LoRA

**LoRA** (Low-Rank Adaptation) congela los pesos del modelo base e inserta matrices pequeñas entrenables (rango bajo) en capas elegidas — aquí, sobre todo las lineales del **language model** (atención / MLP). Solo se actualizan esos adaptadores; el archivo resultante pesa megabytes, no gigabytes.

En este lab usamos **mlx-vlm** (`python -m mlx_vlm.lora` o los wrappers `examples/train_lora.py` / `eval_lora.py`). Qwen3-VL es un modelo de visión+texto: `mlx-lm` solo no alcanza; el camino canónico es mlx-vlm (que a su vez usa el backend MLX).

## Por qué sirve aquí

Queremos que el 8B proponga más a menudo circuitos JSON que:

1. **Compilen** en PennyLane (puertas h/x/y/z/cx/ry).
2. Respeten la **pérdida de energía** de la escena (rebotes).
3. Pasen el árbitro **Jev** (APROBAR).

Sin reentrenar los ~8B parámetros enteros: en la M4 128 GB cabe QLoRA 4-bit + rank 16–64 con batch pequeño.

## Datos

Fuente: `examples/synthetic_physics_dataset.py` → `data/scenes/`.

Cada escena aporta:

- PNG(s) de frames (pelota / forma que cae).
- `meta.json` con verdad física: forma, color, gravedad efectiva, restitución, rebotes, pérdida de energía, trayectoria.

El script `train_lora.py` convierte eso a un dataset tipo chat (imagen + pregunta → JSON de circuito “bueno” + nota). Los circuitos target iniciales se generan con reglas deterministas (firma toy) y/o filas `APROBAR` de `data/experiment_log.jsonl` cuando existan.

Mínimo recomendado antes de un train serio: **≥200 escenas** + **≥50** ejemplos APROBAR en el log (si el log aún es corto, el generador de circuitos-target del script basta para un primer pase).

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
| train-vision | off al inicio | Encender solo si el ground visual falla |
| Dropout LoRA | 0.0–0.05 | |

Tiempo estimado en **M4 128 GB**: **~2–3 horas** para ~200 escenas × 3–5 epochs (QLoRA). Si el dataset crece a 1k, planear 6–10 h o menos iters.

## Criterios de éxito

Sobre un hold-out fijo de **10 escenas de prueba** (`examples/eval_lora.py`):

| Métrica | Base (sin adapter) | Éxito mínimo post-LoRA |
|---------|--------------------|-------------------------|
| JSON parseable | — | ≥ 8/10 |
| Compila PennyLane | — | ≥ 8/10 |
| Jev APROBAR | — | ≥ 7/10 |
| Delta vs base | — | **+20 puntos** en tasa Jev APROBAR **o** compile+parse |

Si no hay mejora ≥20 puntos tras 5 epochs: bajar lr a 1e-4, subir rank a 64, o mezclar más filas APROBAR del experiment_log.

## Secuencia de ejecución

```bash
# 1) Dataset
python examples/synthetic_physics_dataset.py --n-scenes 220 --out data/scenes --seed 42

# 2) (Opcional) ciclo Jev para enriquecer targets
python examples/run_jev_experiment.py --n 5   # cuando el 8B ya cargue

# 3) Train
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

## Fuera de alcance (por ahora)

- Fine-tune completo de pesos.
- Entrenar en la Studio (36 GB): usar 2B/4B Thinking allí, no el 8B.
- Subir adapters a la nube: todo local / este repo.
