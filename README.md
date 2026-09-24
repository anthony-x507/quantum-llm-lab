# quantum-llm-lab

Lab mínimo para un **clúster de dos Macs Apple Silicon** con visión + razonamiento nativo (*Thinking*) + simulador cuántico.

| Máquina | RAM · disco | Modelo fijado | Rol |
|---------|-------------|----------------|-----|
| **Mac M4** | 128 GB · 1 TB | **Qwen3-VL-8B-Thinking** (≈12 GB en 4-bit) | Modelo principal: ve imagen/video, propone ramas de decisión, razona por cadena de pensamiento. Corre **junto** al simulador cuántico. |
| **Mac Studio** | 36 GB · 500 GB | **Qwen3-VL-2B-Thinking** (preferido) o **4B-Thinking** | Segunda pasada: verifica visualmente las ramas de la M4 y las rankea **antes** de mandarlas al simulador. |

Config canónica: [`cluster/cluster.yaml`](cluster/cluster.yaml). Todo **local** (MLX), sin nube de pago. Punto de partida para iterar - no producto terminado.

## Loop completo del clúster

```
visión (frames sintéticos caída/gravedad)
    → LLM 8B en M4 (piensa + propone hipótesis/ramas)
        → LLM chico en Studio (verifica visual + rankea)
            → simulador cuántico (PennyLane / Qiskit) chequea consistencia física
                → feedback al 8B para corregir
```

1. **Visión** - genera frames sintéticos de pelota en caída (`vision/` + `examples/vision_grounding.py`).
2. **Razonar (M4, 8B Thinking)** - el 8B ve el grounding, abre varias ramas de decisión y escribe pensamiento explícito.
3. **Rankear (Studio, 2B/4B Thinking)** - el modelo chico relee frames + ramas y puntúa / filtra antes del simulador.
4. **Cuántico** - PennyLane (o Qiskit) verifica consistencia física toy; sale `quantum_report.json`.
5. **Feedback** - el reporte vuelve al 8B en la M4 para corregir hipótesis.
6. **LoRA (opcional)** - pares de entrenamiento desde `meta.json` (ground truth) vs hipótesis del modelo; ver sección dataset sintético abajo.

## Qué incluye (código existente, sin romper)

1. **Simulador cuántico** (PennyLane, CPU).
2. **Puente LLM → circuito** (`examples/llm_quantum_bridge.py`): stub `--demo` o MLX `--mlx`.
3. **Capa de visión** (`vision/` + `examples/vision_grounding.py`):
   - Frames sintéticos de pelota que cae (gravedad + rebotes con pérdida de energía).
   - JSON estructurado (`--demo` = física conocida; `--mlx` = VLM vía `mlx-vlm`).
4. **Config de clúster** (`cluster/cluster.yaml`): roles, modelos, tamaños RAM y pasos del loop.
5. **Dataset sintético multi-eje** (`examples/synthetic_physics_dataset.py`): 200+ escenas PNG + `meta.json` (forma, color, material, superficie, gravedad, trayectoria) para el loop LoRA.

## Instalación

```bash
git clone https://github.com/anthony-x507/quantum-llm-lab.git
cd quantum-llm-lab
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
# En Mac Apple Silicon, además:
pip install mlx mlx-lm mlx-vlm
```

## Modelos MLX fijados

| Máquina | Hugging Face (MLX) sugerido | Parámetros | RAM aprox. 4-bit |
|---------|-----------------------------|------------|------------------|
| M4 | `mlx-community/Qwen3-VL-8B-Thinking-4bit` | 8B | ~12 GB |
| Studio | `mlx-community/Qwen3-VL-2B-Thinking-4bit` | 2B | ~3 GB |
| Studio (alt.) | `mlx-community/Qwen3-VL-4B-Thinking-4bit` | 4B | ~6 GB |

Familia Alibaba **Qwen3-VL Thinking** (densos también 32B; MoE 30B-A3B y 235B-A22B - no caben en este clúster). La más chica con visión + thinking nativo es **2B-Thinking**.

## Corridas rápidas

### Solo simulador + LLM stub

```bash
python examples/llm_quantum_bridge.py --demo
```

### Visión sintética (sin descargar VLM)

```bash
python examples/vision_grounding.py --demo
# Frames PNG + physics_trace.json + grounding.json en examples/out_frames/
```

### Visión → puente cuántico (pipeline)

```bash
python examples/vision_grounding.py --demo --pipeline
```

### Visión + Thinking en MLX

**M4 (128 GB) - principal 8B Thinking:**

```bash
python examples/vision_grounding.py --mlx \
  --model mlx-community/Qwen3-VL-8B-Thinking-4bit
```

**Mac Studio (36 GB) - verificador 2B (o 4B):**

```bash
python examples/vision_grounding.py --mlx \
  --model mlx-community/Qwen3-VL-2B-Thinking-4bit
# alternate:
#   --model mlx-community/Qwen3-VL-4B-Thinking-4bit
```

Luego pasar el grounding al puente:

```bash
python examples/llm_quantum_bridge.py --demo \
  --context-file examples/out_frames/grounding.json
# o con LLM real en M4:
python examples/llm_quantum_bridge.py --mlx \
  --context-file examples/out_frames/grounding.json
```

## Cómo repartir la carga

```
┌──────────────────────────────────┐   red local    ┌─────────────────────────────────┐
│ Mac M4 (128 GB · 1 TB)           │ ◄────────────► │ Mac Studio (36 GB · 500 GB)     │
│ • Frames sintéticos (opcional)   │  scp/SMB/NFS   │ • Rankea ramas de la M4         │
│ • Qwen3-VL-8B-Thinking (~12 GB)  │  JSON de ramas │ • Qwen3-VL-2B o 4B-Thinking     │
│ • Simulador PennyLane/Qiskit     │  + feedback    │ • (opcional) simulador si M4    │
│ • Feedback / corrección al 8B    │                │   está saturada                 │
└──────────────────────────────────┘                └─────────────────────────────────┘
```

Flujo mínimo de clúster (manual por ahora):

1. **M4:** visión + 8B Thinking → escribe `cluster/out/branches_m4.json` (o `grounding.json` + notas de hipótesis).
2. Copia artefactos a la Studio (AirDrop, `scp`, carpeta compartida).
3. **Studio:** 2B/4B Thinking verifica visualmente y rankea → `cluster/out/ranked_studio.json`.
4. **M4 (preferido):** `llm_quantum_bridge.py` con el ranking; genera `quantum_report.json`.
5. **M4:** reinyecta el reporte al 8B para corregir.

Si no quieres repartir: corre `--demo` en cualquiera; no descarga modelos.

Detalle máquina a máquina: ver `cluster/cluster.yaml`.

## Dataset sintético multi-eje (200+ escenas)

Generador local (Pillow + numpy, sin APIs de pago) que produce escenas visuales variadas para alimentar el loop del clúster y, más adelante, pares LoRA:

```
visión (data/scenes/scene_XXXX/*.png + meta.json)
    → 8B Thinking en M4 (hipótesis / ramas sobre física observada)
        → Studio 2B/4B Thinking (verifica visual + rankea)
            → simulador cuántico (consistencia toy)
                → feedback al 8B
                    → pares LoRA: ground truth (meta.json) vs hipótesis del modelo
```

### Generar el dataset

```bash
pip install pillow numpy   # ya en requirements.txt
python examples/synthetic_physics_dataset.py
# defaults: --n-scenes 220 --out data/scenes --seed 42 --frames-per-scene 30
```

Flags útiles:

```bash
python examples/synthetic_physics_dataset.py --n-scenes 280 --out data/scenes --seed 42
python examples/synthetic_physics_dataset.py --n-scenes 3 --frames-per-scene 24   # smoke
```

Salida por escena (`data/scenes/scene_XXXX/`):

- `frame_0000.png` ... PNG RGB 160x120 (sin display; Agg/Pillow)
- `meta.json` - `shape`, `color`, `size`, `material`, `surface`, `gravity_condition`, `trajectory` por frame (`x,y,vx,vy`), `governing_law`, `objects[]` si hay colisión multi-cuerpo, `seed`

Global:

- `data/scenes/SUMMARY.json` + `SUMMARY.md` - conteos por eje

### Ejes de variación

| Eje | Valores |
|-----|---------|
| shape | square, circle, triangle, rectangle, irregular_polygon |
| color | red, blue, green, yellow |
| size | small, medium, large |
| material | dense, light, hollow (masa / restitución) |
| surface | hard_elastic_floor, soft_lossy_floor, ramp, curve |
| gravity_condition | vacuum_freefall, air_drag, lateral_wind, mars_g, moon_g |
| multi-object | ~30% de escenas con colisiones 2 cuerpos |

Determinista con `--seed`. Los PNG/JSON generados **no** se suben al repo (ver `.gitignore`); solo el script + `data/scenes/.gitkeep`.

### Cómo alimenta el fine-tune LoRA

1. Correr el generador en M4 o Studio → `data/scenes/`.
2. El 8B ve frames y escribe hipótesis (g, restitución, drag, viento, etc.).
3. Studio rankea ramas; el paso cuántico chequea consistencia.
4. Comparar hipótesis vs `meta.json` / `governing_law` → pares (prompt visual + respuesta corregida) para LoRA en las ramas 8B.
5. Re-inyectar el adaptador en el loop visión → reason → rank → quantum → feedback.

## Frames sintéticos (sin video real)

El generador integra caída 1D + rebotes con restitución < 1 (pérdida de energía) y escribe PNG en escala de grises:

```bash
python -c "from vision.synthetic_fall import generate_falling_ball_frames; generate_falling_ball_frames('examples/out_frames', n_frames=48)"
ls examples/out_frames/frame_*.png | head
```

Parámetros útiles en código: `g`, `restitution`, `n_frames`, tamaño `width`×`height`.

## Estructura

```
quantum-llm-lab/
├── README.md
├── requirements.txt
├── pyproject.toml
├── cluster/
│   └── cluster.yaml                 # roles, modelos, loop M4↔Studio
├── data/
│   └── scenes/                      # generado (gitignored) + .gitkeep
├── vision/
│   ├── synthetic_fall.py            # pelota 1D + gravedad + PNG
│   └── grounding.py                 # demo físico o mlx-vlm
└── examples/
    ├── llm_quantum_bridge.py
    ├── vision_grounding.py
    ├── synthetic_physics_dataset.py # 200+ escenas multi-eje → LoRA
    └── out_frames/                  # generado al correr
```

## Notas

- PennyLane en CPU; MLX / mlx-vlm usan Apple Silicon. Qiskit se puede cablear en el mismo paso `quantum` del YAML.
- El circuito cuántico es una **analogía toy** (correlación / atenuación), no una simulación literal de mecánica clásica.
- Si el VLM devuelve JSON inválido, el modo MLX puede caer a la traza física sintética.
- El loop de varias ramas + autoevaluación entre máquinas es **orquestación** (JSON + transferencia); el thinking nativo vive dentro de cada modelo Thinking.

## Licencia

MIT

## Fine-tune con LoRA

Plan: [`docs/lora_plan.md`](docs/lora_plan.md). Wrappers: `examples/train_lora.py`, `examples/eval_lora.py`.

**Cuándo:** ~200+ escenas mixtas (caídas, figuras nuevas, entrelazamiento, superposición) + 8B 4-bit en la M4.

**Qué esperar:** ~2–3 h (rank 32, 3 epochs). Adapter en `data/lora_adapter/`. Éxito = +20 pts Jev APROBAR en 10 escenas vs base.

```bash
python examples/synthetic_physics_dataset.py --n-scenes 280 --out data/scenes --seed 42
python examples/train_lora.py --rank 32 --alpha 32 --lr 2e-4 --epochs 3
python examples/eval_lora.py --adapter data/lora_adapter --n-test 10
```

Carga: `load(..., adapter_path="data/lora_adapter")` con mlx-vlm.

