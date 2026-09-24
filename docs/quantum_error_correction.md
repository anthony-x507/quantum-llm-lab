# Corrección de errores cuánticos (QEC) aplicada a robustez del LLM

Módulo **experimental** del Agent Lab. No es un QEC de hardware real: es una **inspiración** (códigos de superficie / Shor) para detectar y “corregir” corrupción en el flujo de razonamiento del 8B (Qwen3-VL-Thinking) frente a prompts engañosos.

Documento hermano del plan LoRA: ver **Fase 3** en [`docs/lora_plan.md`](lora_plan.md). Implementación demo: [`examples/qec_robustness.py`](../examples/qec_robustness.py).

---

## 1. Cómo funcionan los códigos de error cuántico

Un qubit físico se corrompe: ruido térmico, descoherencia, puertas imperfectas. Un **código de corrección** reparte la información lógica en varios qubits físicos y usa **mediciones de síndrome** (que no revelan el estado lógico) para detectar qué error ocurrió y aplicar una corrección.

### Código de Shor (idea)

- 9 qubits físicos protegen **1** qubit lógico.
- Corrige un bit-flip (X) **o** un phase-flip (Z) en un qubit (y, en el esquema completo, ambos tipos).
- Triplica la información en dos capas (repetition + dual basis).

### Código de superficie (idea, el que usamos en la demo)

- Qubits en una **rejilla 2D**. Aquí: **3×3** qubits de datos (demo pequeña).
- **Estabilizadores** Z (caras / plaquetas) y X (vértices) miden paridades.
- El patrón de mediciones (= **síndrome**) apunta a qué qubit(s) sufrieron X o Z.
- Se aplica la corrección Pauli correspondiente **sin** medir el estado lógico útil.

Propiedades clave que copiamos por analogía:

| QEC real | Qué hace |
|----------|----------|
| Encoding | Estado lógico → muchos físicos |
| Syndrome | Detecta error **sin** colapsar la info lógica |
| Decode + correct | Mapa síndrome → Pauli a aplicar |
| Threshold | Por debajo de cierta tasa de error, el lógico sobrevive |

---

## 2. Analogía con un LLM

| Concepto cuántico | Analogía en el 8B |
|-------------------|-------------------|
| Qubit (físico) | Dimensión / canal de una **representación interna** (activación de capa, embedding de prompt, “firma” de coherencia) |
| Estado lógico | La **intención coherente** de la respuesta (seguir la escena física / Bell / superposición sin saltar a jailbreak) |
| Corrupción (X/Z) | **Input adversarial**: prompt que intenta manipular, invertirse, o empujar al modelo fuera de su política de razonamiento |
| Descoherencia | Drift de activaciones: el vector interno se aleja del “estado de referencia” coherente |
| Medición de síndrome | Monitor de **coherencia**: comparar activaciones actuales vs baseline de prompts seguros |
| Corrección Pauli | **Revertir** la representación hacia el estado coherente (o regenerar con prompt saneado / system reinject) **antes** de emitir tokens |

Importante: no afirmamos que el 8B “tenga qubits”. Es un **diseño inspirado** para robustez: detectar drift y revertir, no un decoder de superficie en producción de MLX.

---

## 3. Diseño concreto del detector cuántico-inspirado

Pipeline en tres bloques (implementado en miniatura en `qec_robustness.py`):

### (a) Monitoreo de coherencia durante la inferencia

1. Definir un **estado de referencia** \( |\psi_0\rangle \) (o vector clásico \( r_0 \)) a partir de un prompt “limpio” de la misma tarea (ej. describir una escena de caída).
2. En cada paso de razonamiento (o al final del prefill), proyectar la representación interna a un vector de **9 amplitudes** (rejilla 3×3) — en la demo: hash/embedding toy del texto del prompt + historial.
3. Codificar ese vector como estado (o como patrón de errores relativos a \( r_0 \)) sobre el código de superficie simulado.

### (b) Detección de manipulación (drift → síndrome)

1. Comparar \( r \) vs \( r_0 \): si la distancia supera un umbral, inyectar (o interpretar) **errores Pauli** en los qubits correspondientes a las dimensiones que más se desviaron.
2. Medir estabilizadores → **síndrome** \( s \).
3. Si \( s \neq 0 \): hay corrupción detectada. Clasificar como “prompt engañoso / adversarial drift”.

En la demo, un prompt adversarial se modela **explícitamente** como flip de 1–2 qubits; el síndrome debe ser no trivial y el decoder debe nombrar el qubit corrupto.

### (c) Reversión a estado coherente antes de responder

1. Decoder: síndrome → operadores de corrección \( C \).
2. Aplicar \( C \) al estado simulado → vuelve a \( |\psi_0\rangle \) (o a distancia &lt; ε).
3. En el LLM real (siguiente iteración del módulo):  
   - **Opción A:** reinyectar system prompt + resumen de la tarea limpia.  
   - **Opción B:** descartar el prefijo envenenado y regenerar.  
   - **Opción C:** atenuar capas (no implementado aquí) hacia activaciones de referencia.

La demo demuestra A en miniatura: tras corregir, el “flujo de razonamiento” vuelve a la respuesta coherente asociada al prompt limpio.

---

## 4. Criterios de éxito (módulo QEC)

| Test | Pasa si |
|------|---------|
| Síndrome cero en prompt limpio | Sin errores inyectados → síndrome trivial |
| Síndrome no trivial bajo ataque | Prompt adversarial → síndrome ≠ 0 |
| Corrección restaura estado | Tras decoder, fidelidad / overlap con referencia ≥ umbral |
| Tests automatizados | `python examples/qec_robustness.py --self-test` exit 0 |

Dependencia: **PennyLane** (ya en `requirements.txt` del lab). No requiere GPU ni el 8B cargado para la simulación del código; el cableado vivo al 8B es Fase 3.b (después de LoRA básico).

---

## 5. Límites honestos

- Rejilla 3×3 es **pedagógica**, no un surface code con distancia de código de producción.
- El “embedding” del prompt en la demo es **toy** (no lee activaciones reales del 8B vía MLX).
- No sustituye filtros de seguridad clásicos (deny-list, Jev, políticas de tool-use); es una capa experimental adicional.
