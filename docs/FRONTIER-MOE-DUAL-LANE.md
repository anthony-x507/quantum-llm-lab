# FRONTIER C1 — MoE dual-lane router

**Repo:** `anthony-x507/quantum-llm-lab`  
**Branch:** `frontier/moe-dual-lane`  
**Script:** `examples/moe_dual_lane_router.py`  
**Artifact:** `data/frontier_moe_dual_lane_smoke.json`  
**SSOT map:** `docs/FRONTIER-RAZONAMIENTO-MAPA.md` §C1  
**Written:** 2026-09-24 ~09:30 ET · Mac-139

---

## Claims (cannot-claim)

- **NO** quantum-advantage claims.
- The optional `--vqc-router` is a **CPU PennyLane simulation** ablation (AngleEmbedding on `default.qubit`). It does **not** prove QPU speedup or better reasoning.
- Router metrics are **usability / own-delta** on Código-vivo pillars only.
- Anti-contam: router prompts never include eval GT labels; compare gold **post-hoc** only.
- `data/lora_adapter/` remains **READ-ONLY** (never write/overwrite).

---

## Why this exists

Código-vivo baseline (`data/BENCHMARK_CODIGO_VIVO.md`, 2026-09-24 05:00 ET):

| Pillar | Base | Single ent adapter | Δ |
|--------|------|--------------------|---|
| Python solve_rate | 0.062 | **0.000** | −0.062 |
| Entanglement label/energy/compile | 0.000 | **1.000** | +1.000 |
| Vision accuracy | 0.900 | **0.700** | −0.200 |

The entanglement LoRA **specializes** circuit JSON / Jev and **hurts** executable Python if applied globally. MoE dual-lane keeps ent expert **off** Python/chat.

---

## How it works

```
prompt ──► route(prompt) ──► lane ∈ {ent, python, vision, base}
                │
                ▼
         adapter_path_for(lane) ──► Path | None
```

### Lanes → adapters

| Lane | Adapter | Notes |
|------|---------|-------|
| `ent` | Prefer `data/lora_adapter_ent2/` if complete; else `lora_adapter_ent/`; else RO `lora_adapter/` **read-only** | Never write RO |
| `python` | `None` (base VLM) | **Hard rule:** ent LoRA never applied |
| `vision` | **Default `None` (base)** | `video_f1` opt-in via `MOE_VISION_ADAPTER=video` (ablation: −30 pp on CV math set) |
| `base` | `None` | Chat / default |

### Router methods

1. **Heuristic (default)** — keyword rules:
   - `circuit|gates|PennyLane|entrelaz|qubit|Bell|…` → `ent`
   - `python|def|ONLY code|print(|…` → `python` (**wins over ent** unless explicit circuit-JSON ask)
   - `image|frame|visión|Look at the image|…` → `vision`
   - else → `base`
2. **`--mlp`** — tiny bag-of-words logistic (hand weights, no sklearn / no eval GT training). Safety: heuristic `python` cannot be overridden to `ent`.
3. **`--vqc-router`** — PennyLane `AngleEmbedding` (4 wires) + ring CNOTs on CPU; blended with heuristic. **Ablation only, default OFF.**

### API

```python
from moe_dual_lane_router import route, adapter_path_for

lane = route("Write a Python program that prints 2**10")  # → "python"
path = adapter_path_for(lane)  # → None
```

### CLI

```bash
# 12-fixture smoke (CPU)
.venv/bin/python examples/moe_dual_lane_router.py --smoke

# Optional MLP / VQC ablations
.venv/bin/python examples/moe_dual_lane_router.py --smoke --mlp
.venv/bin/python examples/moe_dual_lane_router.py --smoke --vqc-router

# Código-vivo with per-pillar routed adapters (GPU / MLX; skips if train live)
.venv/bin/python examples/moe_dual_lane_router.py --bench-codigo-vivo
```

Bench wiring: imports `bench_codigo_vivo` pillar runners + `_load_vlm`; injects the adapter chosen per lane. Does **not** rewrite the whole bench. If `mlx_vlm.lora` / `qlora-ent-v6` / `train_lora` is live, bench is skipped (CPU smoke only).

---

## Success gate (Código-vivo)

Measure routed run vs stored baseline in `BENCHMARK_CODIGO_VIVO.json`:

1. **Python ≥ base** solve_rate (ent LoRA must not poison code)
2. **Ent ≥ 0.95** label_acc (expert lane still works)
3. **Vision** not worse than **−5 pp** vs base (if measured)

`gate_pass` is written into the artifact JSON under `bench.gate`.

---

## Smoke fixtures

12 prompts (3× ent, 3× python, 3× vision, 3× base). Target: **12/12** expected lane. Document any misses in the artifact `smoke.rows` (`ok: false`).

---

## Paths

| Item | Path |
|------|------|
| Router | `examples/moe_dual_lane_router.py` |
| Docs | `docs/FRONTIER-MOE-DUAL-LANE.md` |
| Smoke/bench artifact | `data/frontier_moe_dual_lane_smoke.json` |
| Baseline | `data/BENCHMARK_CODIGO_VIVO.{json,md}` |
| RO quantum adapter | `data/lora_adapter/` |
| Ent expert (preferred) | `data/lora_adapter_ent2/` |

---

## Measured (2026-09-24 ~09:33 ET)

Smoke: **12/12** heuristic (also 12/12 MLP + VQC ablation).

Routed Código-vivo vs stored baseline:

| Pillar | Baseline base | Routed | Gate |
|--------|---------------|--------|------|
| Python solve_rate | 0.0625 | **0.0625** (lane=python, adapter=None) | ≥ base ✓ |
| Ent label_acc | 0.000 (base) / 1.0 (ent RO) | **1.000** (lane=ent, `lora_adapter_ent2`) | ≥ 0.95 ✓ |
| Vision accuracy | 0.900 | **0.900** (lane=vision, adapter=None) | ≥ −5 pp ✓ |

`gate_pass`: **true**

Ablation: vision + `lora_adapter_video_f1` → 0.600 (−30 pp) — not default.

Primary win vs single-adapter Código-vivo: Python recovers from **0.000 → 0.0625** by **not** applying ent LoRA to code prompts; Ent stays 1.0.

---

## Related

- Lock: `docs/LOCK-ANTI-CONTAMINATION.md`
- Map: `docs/FRONTIER-RAZONAMIENTO-MAPA.md` (C1 IMPLEMENT NOW)
- Bench: `examples/bench_codigo_vivo.py`
