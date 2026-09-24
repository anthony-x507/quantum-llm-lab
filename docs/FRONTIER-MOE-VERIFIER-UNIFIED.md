# Frontier C3 — MoE dual-lane + Python verifier (Código-vivo unified)

**Branch:** `frontier/moe-verifier-codigo-vivo`  
**Claim scope:** routing usability + classical `python -I` exec repair. **No quantum-advantage claims.**

Unifies:

| Piece | Branch / commit (upstream) | Role |
|-------|----------------------------|------|
| MoE dual-lane | `frontier/moe-dual-lane` @ `fc9d50a` | Route `ent \| python \| vision \| base`; **never** apply ent LoRA to Python/chat |
| Gold-free Python verifier | `frontier/verifier-python-repair` @ `ea4d361` | Propose → `python -I` oracle → revise ≤2 with stderr only |

## Script

```bash
python examples/moe_verifier_codigo_vivo.py --smoke
python examples/moe_verifier_codigo_vivo.py --cpu-eval --limit 16
python examples/moe_verifier_codigo_vivo.py --replay --limit 16
python examples/moe_verifier_codigo_vivo.py --mlx-eval --limit 3   # optional; never blocks ship
```

Also still available standalone:

- `examples/moe_dual_lane_router.py`
- `examples/python_verifier_loop.py`

## Comparative paths (Python pillar)

| Path | Meaning |
|------|---------|
| **(a) single-shot no-MoE** | First-shot only, `rounds=0`, no router |
| **(b) MoE alone** | Router selects lane; Python lane = first-shot **without** ent adapter |
| **(c) verifier alone** | Forced python lane + repair ≤2 (gold-free local fix / stderr) |
| **(d) MoE+verifier unified** | Router; Python lane gets verifier loop; Ent/Vision = **RO** adapter select only |

Metrics: `solve_rate_single`, `solve_rate_loop`, `repair_success_rate`, `Δ vs (a)`, `prompt_touches_gt`.

## Anti-contamination LOCK

- Ground-truth / `expected_stdout` **never** enters inference or revision prompts.
- Revision context = task prompt + previous code + stderr/traceback summary only.
- Evidence JSON must carry `prompt_touches_gt: false` (and `anti_contamination.prompt_touches_gt: false`).
- Python lane adapter is always `None` (base). Ent LoRA is not applied to code prompts.
- `data/lora_adapter/` is **READ-ONLY** — this frontier never writes/overwrites it. Ent2/classical/video adapters are read for lane mapping only.

See `docs/LOCK-ANTI-CONTAMINATION.md` when present on the tree.

## Prior live numbers (honest, from shipped JSONs)

From `data/frontier_moe_dual_lane_smoke.json` (MoE routed Código-vivo):

| Pillar | n | MoE routed | Notes |
|--------|---|------------|-------|
| Python | 16 | **0.0625** | Win vs applying ent LoRA to code (was 0) |
| Entanglement | 12 | **label_acc 1.0** (ent2) | Gate ≥0.95 |
| Vision | 10 | **0.900** | Base; not worse than −5pp |

From verifier:

| Run | n | single | loop | Δ |
|-----|---|--------|------|---|
| mlx Studio smoke | 3 | 0.000 | **1.000** | +1.000 |
| replay n=16 | 16 | 0.062 | **0.688** | +0.625 |
| cpu heuristic smoke | 5 | 0.000 | **1.000** | +1.000 |

Unified CPU/heuristic smoke re-measures (a)–(d) on the same local items; live mlx for path (d) is optional and must not block the ship if GPU/weights are unavailable.

## Evidence artifacts

| File | Contents |
|------|----------|
| `data/frontier_moe_verifier_cpu_smoke.json` | Router 12/12 + paths (a)–(d) heuristic |
| `data/frontier_moe_verifier_replay.json` | Replay proposer comparative (if fixtures present) |
| `data/frontier_moe_verifier_mlx_smoke.json` | Optional Studio live |
| `data/frontier_moe_verifier_unified.json` | Optional full dump |

## Gate (informal)

Ship-OK when:

1. Branch pushed to `origin` (no merge to `main`).
2. CPU/heuristic smoke **PASS** (`prompt_touches_gt=false`, router smoke complete, `ent_never_on_python`).
3. Numbers reported honestly even if unified does not win every column.

## Machines

- **Mac-139** (`074c6626-…`): implement / commit / CPU smoke.
- **Mac Studio** (`8e12e5c3-…`): optional mlx live 8B for Python lane.

## What this does NOT do

- No merge to `main`.
- No writes under `data/lora_adapter/`.
- No quantum-advantage marketing.
- No Cursor Cloud Agents for this unify.

## Mixed-live extension

See **`docs/FRONTIER-MOE-VERIFIER-MIXED-LIVE.md`** (`frontier/moe-verifier-mixed-live`):
mixed Python+Ent+Vision scoreboard so MoE Δ is visible (ent 0→1.0; overall +0.33).

