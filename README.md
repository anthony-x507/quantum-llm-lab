# quantum-llm-lab

Lab mínimo para experimentar en un **Mac Apple Silicon (M4, mucha RAM)** con:

1. Un **LLM pequeño local** vía [MLX](https://github.com/ml-explore/mlx) (sin nube de pago).
2. Un **simulador cuántico en CPU** ([PennyLane](https://pennylane.ai/)).
3. Un **script puente**: el LLM propone un circuito de 2–3 qubits y el simulador lo ejecuta.

No es un producto terminado: es un punto de partida para iterar.

## Requisitos

- macOS en chip Apple (M1/M2/M3/M4).
- Python 3.10+ (recomendado 3.11 o 3.12).
- Conexión a internet **solo la primera vez** si usas `--mlx` (descarga del modelo). El modo `--demo` no necesita modelo.

## Instalación paso a paso

```bash
git clone https://github.com/anthony-x507/quantum-llm-lab.git
cd quantum-llm-lab

python3 -m venv .venv
source .venv/bin/activate

# Simulador cuántico (siempre)
pip install -U pip
pip install -r requirements.txt

# LLM local MLX (solo en Mac Apple Silicon)
pip install mlx mlx-lm
```

Si `pip install mlx` falla, confirma que estás en Darwin arm64:

```bash
uname -m   # debe decir arm64
python3 -c "import platform; print(platform.platform())"
```

## Primera corrida (sin descargar LLM)

Prueba el simulador con un stub que imita la propuesta del modelo:

```bash
python examples/llm_quantum_bridge.py --demo
```

Deberías ver probabilidades sobre estados `|00>`, `|01>`, `|10>`, `|11>` y una suma cercana a `1.0`.

## Corrida con LLM local (MLX)

Modelo por defecto: `mlx-community/Llama-3.2-3B-Instruct-4bit` (~3B cuantizado, razonable en M4 con mucha RAM). Puedes cambiarlo.

```bash
python examples/llm_quantum_bridge.py --mlx
```

Otro prompt / otro modelo:

```bash
python examples/llm_quantum_bridge.py --mlx \
  --model mlx-community/Llama-3.2-3B-Instruct-4bit \
  --prompt "Propón un circuito de 3 qubits con Hadamard en todos y un CNOT de 0 a 1."
```

La primera descarga del modelo puede tardar y ocupar varios GB en disco. Después queda en caché local.

## Qué hace el script

1. **Propone** un circuito en JSON (`n_qubits` + lista de `gates`).
2. **Construye** el circuito en PennyLane (`default.qubit`, CPU).
3. **Mide** probabilidades de cada base computacional e imprime una barra ASCII.

Puertas soportadas en este lab: `h`, `x`, `y`, `z`, `cx`, `ry`.

## Estructura

```
quantum-llm-lab/
├── README.md
├── requirements.txt
├── pyproject.toml
└── examples/
    └── llm_quantum_bridge.py
```

## Notas

- PennyLane corre en CPU del Mac; no necesitas GPU cloud.
- MLX usa el Neural Engine / GPU unificada del Apple Silicon.
- Si el modelo inventa JSON inválido, el script falla con un mensaje claro: ajusta el prompt o vuelve a `--demo`.
- Qiskit también sirve como simulador; este repo eligió PennyLane por ser liviano. Se puede añadir después.

## Licencia

MIT — úsalo, rómpelo, mejóralo.
