# quantum-llm-lab

Lab mínimo para un **clúster de dos Macs Apple Silicon**:

| Máquina | RAM | Rol sugerido |
|---------|-----|----------------|
| **Mac M4** | 128 GB · 1 TB | Visión grande (Qwen2-VL **7B** 4-bit) + LLM 3B–7B |
| **Mac Studio** | 36 GB · 500 GB | Visión chica (Qwen2-VL **2B** 4-bit) o solo `--demo` + simulador |

Todo **local**, sin nube de pago. Punto de partida para iterar — no producto terminado.

## Qué incluye

1. **Simulador cuántico** (PennyLane, CPU).
2. **Puente LLM → circuito** (`examples/llm_quantum_bridge.py`): stub `--demo` o MLX `--mlx`.
3. **Capa de visión** (`vision/` + `examples/vision_grounding.py`):
   - Genera **frames sintéticos** de una pelota que cae (gravedad + rebotes con pérdida de energía).
   - Los describe en JSON estructurado (`--demo` = física conocida; `--mlx` = Qwen2-VL vía `mlx-vlm`).
   - Ese texto grounded alimenta al LLM; el simulador cuántico ejecuta una “firma” toy del fenómeno.

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

### Visión con VLM real (MLX)

**En la M4 (128 GB)** — modelo grande:

```bash
python examples/vision_grounding.py --mlx \
  --model mlx-community/Qwen2-VL-7B-Instruct-4bit
```

**En la Mac Studio (36 GB)** — modelo chico:

```bash
python examples/vision_grounding.py --mlx \
  --model mlx-community/Qwen2-VL-2B-Instruct-4bit
```

Luego pasar el grounding al puente:

```bash
python examples/llm_quantum_bridge.py --demo \
  --context-file examples/out_frames/grounding.json
# o con LLM real:
python examples/llm_quantum_bridge.py --mlx \
  --context-file examples/out_frames/grounding.json
```

## Clúster: qué corre en cada máquina

```
┌─────────────────────────────┐     red local      ┌──────────────────────────┐
│ Mac M4 (128 GB)             │ ◄───────────────► │ Mac Studio (36 GB)       │
│ • Generar frames (opcional) │   NFS/SMB/scp     │ • Simulador PennyLane    │
│ • VLM Qwen2-VL 7B           │   grounding.json  │ • LLM 3B o solo --demo   │
│ • (opcional) LLM 7B         │                   │ • VLM 2B si hace falta   │
└─────────────────────────────┘                   └──────────────────────────┘
```

Flujo mínimo de clúster:

1. **M4:** `python examples/vision_grounding.py --mlx --model …7B…`
2. Copia `examples/out_frames/grounding.json` a la Studio (AirDrop, `scp`, carpeta compartida).
3. **Studio:** `python examples/llm_quantum_bridge.py --demo --context-file …/grounding.json`  
   (o `--mlx` con un 3B si cabe en 36 GB junto al resto).

Si no quieres repartir carga: corre `--demo` en cualquiera; no descarga modelos.

## Frames sintéticos (sin video real)

El generador integra caída 1D + rebotes con restitución &lt; 1 (pérdida de energía) y escribe PNG en escala de grises:

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
├── vision/
│   ├── synthetic_fall.py   # pelota + gravedad + PNG
│   └── grounding.py        # demo físico o mlx-vlm
└── examples/
    ├── llm_quantum_bridge.py
    ├── vision_grounding.py
    └── out_frames/           # generado al correr (gitignored parcialmente)
```

## Notas

- PennyLane en CPU; MLX/MLX-VLM usan Apple Silicon.
- El circuito cuántico es una **analogía toy** (correlación / atenuación), no una simulación literal de mecánica clásica.
- Si el VLM devuelve JSON inválido, el modo MLX puede caer a la traza física sintética.
- Qiskit se puede añadir después; este lab usa PennyLane por ser liviano.

## Licencia

MIT
