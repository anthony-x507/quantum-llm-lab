# ESTUDIO PUNTA DE FLECHA — resumen comprimido

**2026-09-23 ET** · quantum-llm-lab (M4 128GB · Qwen3-VL-8B-Thinking-4bit · PennyLane · Jev)  
Full study (box): `/workspace/quantum-night/ESTUDIO-PUNTA-FLECHA.md` · GPS: `PASO-1-HOY.md`

## Veredicto
- LoRA/QLoRA VLM en MLX es **real** (mlx-vlm.lora + Qwen3-VL 4-bit). Docs: https://github.com/Blaizzy/mlx-vlm/blob/main/mlx_vlm/LORA.MD
- El lab **no** hace quantum advantage: hace LLM→JSON gates→PennyLane + Jev (patrón AgentQ/PennySynth).
- QEC 3×3 del repo = **metáfora pedagógica**. Publishable cercano: SERC (LDPC semantic ECC) https://arxiv.org/abs/2605.28837 — no “surface code del LLM”.

## Bugs tip-of-spear en `train_lora.py`
1. **Fuga de labels** (`domain`/`label`/`entangled`/…) en el user prompt → memorizer de meta, no visión.
2. Faltan `--train-on-completions --grad-checkpoint --gradient-accumulation-steps 4`.
3. Thinking + `max_tokens=220` → JSON truncado.
4. Targets fall casi idénticos (H+CX+RY) → diversity≈0.
5. Eval prompt ≠ train prompt; gold fallback infla métricas.

## KEEP / DROP
**KEEP:** anti-fuga; flags mlx; dataset 280 joint; Jev; métricas parse/compile/Jev-lift/label-acc/diversity/energy-consistency; QEC demo como analogía.  
**DROP:** train-vision; rank64 ciego; Fase4 QEC hooks; claims ventaja cuántica; adapters por dominio.

## Métricas éxito
parse≥0.8 · compile≥0.8 · ΔJev APROBAR ≥+0.20 (fall) · label≥0.7 (quantum) · ≥4 templates fall.

## PASO 1 ahora
Parche `examples/train_lora.py`: quitar gold del summary + flags mlx. Luego `--prepare-only`.  
PASO 2: `synthetic_physics_dataset.py --n-scenes 280`.  
PASO 3: smoke 1 epoch r=16.  
PASO 4: eval limpia.  
PASO 5: diversificar targets; QEC hold.

## Citas clave
- mlx LoRA: https://github.com/Blaizzy/mlx-vlm/blob/main/mlx_vlm/LORA.MD
- QLoRA: https://github.com/artidoro/qlora
- PennySynth: https://arxiv.org/html/2605.25572v2
- SERC: https://arxiv.org/abs/2605.28837
- TN QI-ML: https://spj.science.org/doi/10.34133/icomputing.0061
