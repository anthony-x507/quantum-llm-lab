# Frontier C3b — MoE + verifier MIXTO (Python + Entanglement + Vision)

**Branch:** `frontier/moe-verifier-mixed-live`  
**Upstream:** `frontier/moe-verifier-codigo-vivo` @ `3eeeb33`  
**Claim scope:** routing usability + classical `python -I` exec repair on a **mixed** Código-vivo set. **No quantum-advantage claims.**

## Why mixed?

The python-only unify made **MoE ≈ baseline** (both use base on the python lane). A mixed set forces the MoE Δ to show up via entanglement (base label_acc **0.0** → MoE/ent2 **1.0**) while vision stays base (**0.9**) and python keeps the verifier loop.

## Fixtures

`data/bench_live/mixed_items.json`

| Pillar | n | Notes |
|--------|---|-------|
| Python | ≥8 | Gold-free prompts; `expected_stdout` harness-only |
| Entanglement | ≥8 | Scene prompts; **label never in prompt** |
| Vision (scored) | ≥8 | Image-math; `expected` harness-only |
| Hard-neg router | 10 | Ambiguous / domain hard-negs |

## Scoreboard paths

| Path | Meaning |
|------|---------|
| **(a) baseline** | No MoE: base all pillars; python single-shot |
| **(b) MoE alone** | Route; ent→`lora_adapter_ent2` RO; python/vision→base |
| **(c) verifier-on-python** | No MoE on ent/vis; python repair ≤2 |
| **(d) unified** | MoE + verifier on python lane only |

Ent/vision rates on CPU use **prior-replay** from `BENCHMARK_CODIGO_VIVO.json` + MoE dual-lane live (labeled `metric_source=prior_replay`). Python rates are measured live (heuristic / replay / optional mlx).

## Results (CPU heuristic, n_py=8)

| Path | python | ent label_acc | vision | overall |
|------|--------|---------------|--------|---------|
| (a) baseline | 0.000 | 0.000 | 0.900 | **0.300** |
| (b) MoE alone | 0.000 | **1.000** | 0.900 | **0.633** |
| (c) verifier-on-python | **1.000** | 0.000 | 0.900 | 0.633 |
| (d) unified | **1.000** | **1.000** | 0.900 | **0.967** |

**Δ MoE vs baseline (overall): +0.333** — visible (`moe_delta_visible=true`), driven by entanglement.

Replay (n_py=8): overall (a) 0.342 → (b) 0.675 → (d) 0.967; same MoE Δ +0.333.

Router: pillar **26/26**, hard-neg **10/10**, `ent_never_on_python=true`.

## Anti-contamination

- `prompt_touches_gt: false`
- Ent labels / vision expected / python `expected_stdout` live only under `eval.*`
- Python lane adapter always `None` (never ent LoRA)
- `data/lora_adapter/` **READ-ONLY**

## Script

```bash
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
python examples/moe_verifier_mixed_live.py --smoke
python examples/moe_verifier_mixed_live.py --cpu-eval
python examples/moe_verifier_mixed_live.py --replay
# optional live (lab .venv; Studio preferred when online)
.venv/bin/python examples/moe_verifier_mixed_live.py --mlx-eval --limit 2
```

## Evidence

| File | Contents |
|------|----------|
| `data/frontier_moe_verifier_mixed_cpu.json` | Full CPU scoreboard |
| `data/frontier_moe_verifier_mixed_replay.json` | Replay python + prior ent/vis |
| `data/frontier_moe_verifier_mixed_mlx.json` | Optional mlx (Mac-139 n=2; Studio was offline) |
| `data/frontier_moe_verifier_mixed_unified.json` | Rollup |

## Router polish applied

- Vision arithmetic / explicit `no circuit` beats stray `circuit` tokens (chalkboard hard-neg).
- `Look at the … sequence` recognized as vision.
- Circuit-JSON-from-image fixtures expect **ent** lane (correct MoE behavior).

## Machines

- **Mac-139** (`074c6626-…`): implement / CPU / optional mlx when Studio down.
- **Studio** (`8e12e5c3-…`): preferred mlx 8B when connected (was offline this run).

## What this does NOT do

- No merge to `main`.
- No writes under `data/lora_adapter/`.
- No quantum-advantage marketing.
- No Cursor Cloud Agents.
