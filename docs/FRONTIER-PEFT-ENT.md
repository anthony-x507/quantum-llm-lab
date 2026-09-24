# FRONTIER-PEFT-ENT — Adapter de grafo Clifford–Pauli

Infraestructura (sin train VLM) para condicionar un LLM/VLM con embeddings de circuitos
cuánticos representados como grafos de puertas Clifford/Pauli. Rama: `frontier/circuit-graph`.

**Sin claims de ventaja cuántica.** El grafo/GNN es un *feature encoder* clásico sobre
estructura de circuitos; PennyLane corre en CPU. No se afirma speedup ni Q-advantage.

## 1. Formalismo del grafo (ref. arXiv:2503.14448)

- **Nodos** = puertas del circuito propuesto (`h,x,y,z,cx,ry`). Cada nodo lleva:
  - `gate`, `qubits`, `theta` (si aplica), `pauli` (string Pauli asociado a la acción local).
- **Aristas** = anti-conmutación de Pauli: arista entre nodos *i* y *j* si `[P_i, P_j] ≠ 0`
  (es decir, `{P_i, P_j} = 0` en el soporte solapado). Puertas que conmutan no generan arista.
- Construcción **solo** a partir de gates propuestas (JSON/QASM mínimo). **Nunca** a partir
  de labels GT, `gold`, `collapsed_to`, ni campos de evaluación.

Mapeo Pauli local (lab 1–3 qubits):

| Gate | Pauli tipado |
|------|----------------|
| `h`  | mezcla X/Z → se tipa como `X` en el wire (proxy de flip de base) |
| `x`  | `X` |
| `y`  | `Y` |
| `z`  | `Z` |
| `cx` | control `Z`, target `X` (dos nodos lógicos o un nodo con pauli `ZX` en wires c,t) |
| `ry` | rotación en Y → Pauli `Y` (ángulo en `theta`) |

Bell canónico: `H(0) + CX(0,1)`.

## 2. Encoder GNN → embedding fijo → conditioning

1. `circuit_graph.build_graph(proposal)` → grafo tipado (nodos + aristas anti-comm).
2. `gnn_encoder.encode(graph) → np.ndarray` dim fija (default **64**), message-passing
   2–3 capas, **torch CPU**.
3. `conditioning.PrefixConditioner` / `CrossAttnConditioner` (stubs): proyectan el
   embedding a *prefix tokens* o *keys/values* proyectadas. **No cablean** el VLM real
   (Qwen 8B); solo definen la interfaz para un futuro PEFT/prefix-tuning.

Flujo: `JSON gates → grafo → GNN → emb → conditioner stub → pauli_tool`.

## 3. Tool PennyLane (`pauli_tool`)

Wrapper CPU sobre `default.qubit`:

| Campo | Significado |
|-------|-------------|
| `unitary_ok` | circuito ejecutable sin error; probs suman ≈1 |
| `energy` | ⟨Z⊗Z⟩ (2q) o ⟨Z⟩ (1q); documentado, no Hamiltoniano de problema |
| `fingerprint` | hash corto de probs redondeadas / bitstring dominante |

Smoke Bell: H+CX → probs ~0.5/0.5 en `00`/`11`, `energy` ⟨ZZ⟩ ≈ +1 (estado Bell Φ⁺).

## 4. Loss auxiliar (plan; NO se entrena aquí)

L = L_task + λ_c · L_compile + λ_e · L_energy + λ_d · L_diversity

- **compile**: 1 − unitary_ok (penaliza circuitos inválidos).
- **energy**: |⟨ZZ⟩ − target| o MSE vs energía de referencia del dominio (sin filtrar GT
  como input del grafo).
- **diversidad fingerprints**: incentiva cobertura de firmas distintas en batch.

## 5. Gate dual de aceptación (eval futura)

Aceptar un checkpoint solo si **ambas** se cumplen:

1. **ent** ≥ 0.95 en el set de entanglement del lab.
2. **Python** ≥ baseline del set código vivo (referencia lab: 1/16 ≈ 0.0625 floor;
   el umbral operativo se fija al baseline medido del run, no por debajo).

Sin filtrar ejemplos con labels en el builder de grafos.

## 6. Plan train (NO ejecutar en esta rama)

| Fase | Qué | Est. horas M4 (GPU Metal / MLX) |
|------|-----|----------------------------------|
| (a) Pretrain GNN | grafos sintéticos Bell/random (`synthetic_graphs`) | **2–4 h** |
| (b) Fine-tune conjunto | dataset ent (v7+) + conditioning → Qwen/VLM PEFT | **8–16 h** |
| (c) Eval dual | ent + Python; gate §5 | **1–2 h** |

**Total estimado M4: ~12–22 h** de wall-clock GPU (sin contar colas ni waiters).
Torch CPU sirve para smoke/unitarios; el train real del VLM sigue el stack MLX/LoRA
existente y **no** debe tocar `data/lora_adapter/` en paralelo a runs vivos.

## 7. Riesgos / vetos

| Riesgo | Mitigación |
|--------|------------|
| Leakage GT → grafo | API de builder rechaza kwargs `label`/`gold`/`gt`; test dedicado |
| Torch CPU vs Metal | Smoke/GNN en CPU; train VLM en su carril; no pelear GPU |
| Claims Q-advantage | Prohibidos en docs/PR/commits |
| Contaminar main dirty | Worktree limpio desde `origin/main`; solo archivos frontier |
| Matar trains vivos | No tocar PIDs video/classical/ent |

## 8. Top-3 contexto breve

1. **MoE / routers** — conditioning como “experto” de circuito junto a LoRA de visión.
2. **Quantum-PEFT / QuanTA** — PEFT sobre parámetros cuánticos/ángulos; aquí el PEFT
   es clásico sobre embedding de grafo, no se afirma equivalencia.
3. **Este graph stack** — Clifford–Pauli GNN + tool PennyLane + stubs de prefix/cross-attn
   hacia Qwen 8B (interfaz lista; wiring VLM pendiente).

## 9. Qué falta para train real

- Cablear `PrefixConditioner` / cross-attn al stack LoRA/MLX del lab (Qwen 8B).
- Dataset de grafos sintéticos a escala + collate con emb congelado o joint.
- Loss auxiliar en el loop de train (compile/energy/diversity).
- Eval dual automatizada (ent≥0.95 ∧ Python≥base) sin leakage.
- Decidir freeze vs fine-tune del GNN junto al VLM; checkpoints fuera de
  `data/lora_adapter/` (nuevo dir, p.ej. `data/lora_adapter_circuit_graph/`).
- No lanzar mientras screens video/classical/ent estén vivos en GPU.
