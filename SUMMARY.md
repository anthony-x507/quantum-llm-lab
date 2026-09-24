# quantum-llm-lab — First experiment cycle SUMMARY

**Date:** 2026-09-23 21:24 EDT (America/New_York)  
**Repo:** `/Users/anthony/Documents/quantum-llm-lab` @ `6a73e6a` (origin/main)  
**Machine:** MacBook M4 (local)

## 1) Model smoke (Spanish)

- **Model:** `mlx-community/Qwen3-VL-8B-Thinking-4bit` (4-bit MLX VLM, loaded via `mlx_vlm`)
- **Prompt:** Responde en una frase en español: ¿estás listo para proponer circuitos cuánticos?
- **Reply (Spanish line from model output):** Sí, estoy listo para proponer circuitos cuánticos con entrelazamiento y puertas lógicas.
- **Note:** Thinking variant spent most tokens on chain-of-thought; Spanish confirmation extracted from its draft sentence. First cold download ~17 min (~5.4 GB); subsequent load ~0.7s from HF cache.

## 2) First Jev verdict

- **Verdict:** `APROBAR`
- **Reason:** Circuito válido, consistente con pérdida/escena y probs≈1.
- **Scene:** `scene_0000` — green triangle small material=dense surface=soft_lossy_floor g=mars_g restitution=0.357 multi=False

## 3) Experiment log (5 scenes)

- **Absolute path:** `/Users/anthony/Documents/quantum-llm-lab/data/experiment_log.jsonl`
- **Lines:** 5
- **All verdicts:** scene_0000=APROBAR, scene_0001=APROBAR, scene_0002=APROBAR, scene_0003=APROBAR, scene_0004=APROBAR
- **Proposal source:** all `fallback` this run — model emitted thinking text without parseable circuit JSON within `max_tokens`; `run_jev_experiment` / cycle used demo Bell+RY proposal once per scene (as designed).

## Artifacts

| Path | Role |
|------|------|
| `/Users/anthony/Documents/quantum-llm-lab/data/experiment_log.jsonl` | JSONL experiment log (5 lines) |
| `/Users/anthony/Documents/quantum-llm-lab/examples/jev_arbiter.py` | Jev APROBAR/RECHAZAR arbiter |
| `/Users/anthony/Documents/quantum-llm-lab/examples/run_jev_experiment.py` | 5-scene cycle runner |
| `/Users/anthony/Documents/quantum-llm-lab/data/experiment_scenes` | Synthetic scenes n=5 |
| `/Users/anthony/Documents/quantum-llm-lab/docs/PLAN-MAESTRO.md` | Master plan (pulled with main) |

## Errors / caveats

- Unauthenticated HF Hub downloads (rate-limited / slow xet); no `HF_TOKEN` set.
- Qwen3-VL-**Thinking** often returns CoT instead of bare JSON → fallback proposals; increase `max_tokens` or add anti-think instruction for real LLM proposals next cycle.
- Git: local WIP stashed, `main` fast-forwarded to `6a73e6a`, stash restored (jev scripts + scenes untracked).

## 4) CoT / max_tokens fix cycle (v2) — 2026-09-23 21:27 EDT

**Patches:** `max_tokens` 220→1024 (+ `--max-tokens`), Spanish JSON-only prompt (think ≤2 sentences), strip `<think>` + brace-balanced JSON extract in `run_jev_experiment.propose_circuit_vlm` and `llm_quantum_bridge.parsear_propuesta`; scene-hash varied fallback gates.

**Re-run:** `examples/run_jev_experiment.py --n 2 --log data/experiment_log_v2.jsonl`

| Scene | proposal_source | gates | Jev |
|-------|-----------------|-------|-----|
| scene_0000 | **mlx_vlm** | h,cx,ry(0.4) | APROBAR |
| scene_0001 | **mlx_vlm** | h,cx,ry(0.4) | APROBAR |

- **Score:** 2/2 `proposal_source=mlx_vlm` with valid gates (SUCCESS).
- **First raw_preview snippet (scene_0000):** `Got it, let's see. The problem is to propose a 2-qubit circuit based on the visual scene. The scene has a blue irregular polygon...` — model still opens with English CoT, but with 1024 tokens it finishes and emits parseable circuit JSON (notas in Spanish from the model).
- **Git:** quantum-llm-lab `c08f896` on main; Agent-Lab- mirrored `be4ec62`.

