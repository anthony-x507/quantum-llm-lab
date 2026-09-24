# Frontier C2 — Gold-free Python verifier (propose → exec → revise ≤2)

**When:** 2026-09-24 ~09:33 ET  
**Branch:** `frontier/verifier-python-repair`  
**Claim:** NO quantum advantage. Classical `python -I` exec oracle only.  
**Prototype:** `examples/python_verifier_loop.py`  
**Pattern:** Extends hybrid oracle (`examples/hybrid_oracle_loop.py`) to Código-vivo Python.

## Flow

1. **Propose** — heuristic CPU / `--replay` from `BENCHMARK_CODIGO_VIVO.json` / optional `--mlx-eval`.
2. **Verify** — subprocess `python -I` in temp cwd, stripped env (no network keys), timeout 5–10s.
3. **Revise ≤2** — on exec fail, append **stderr/traceback summary** to revision prompt.  
   **Never** inject `expected_stdout` / gold solution (anti-contam LOCK).
4. Local gold-free fix (CPU): strip trailing prose / AST-prefix trim / re-extract fences — mirrors hybrid `build_local_fix`.

## CLI

```bash
python examples/python_verifier_loop.py --self-test
python examples/python_verifier_loop.py --cpu-eval --limit 5 --rounds 2
python examples/python_verifier_loop.py --replay --rounds 2 \
  --out data/frontier_python_verifier_replay_n16.json
python examples/python_verifier_loop.py --mlx-eval --limit 3   # Studio preferred; skip if GPU busy / weights missing
```

## Metrics (this run)

| path | n | solve_rate_single | solve_rate_loop | Δ | repair_success_rate | prompt_touches_gt |
|------|---|-------------------|-----------------|---|---------------------|-------------------|
| cpu smoke | 5 | 0.000 | 1.000 | +1.000 | 1.000 | false |
| replay smoke | 5 | 0.200 | 1.000 | +0.800 | 1.000 | false |
| **mlx live Studio smoke** | 3 | 0.000 | 1.000 | +1.000 | 1.000 | false |
| cpu heuristic n=16 | 16 | 0.000 | 1.000 | +1.000 | 1.000 | false |
| replay base n=16 | 16 | 0.062 | 0.688 | +0.625 | 0.667 | false |

Sources: `data/frontier_python_verifier_*.json`  
Bench set: `data/bench_live/python_items.json` (N=16) · single-shot baseline in bench was base solve_rate≈0.062 (1/16).

### Honest note

- **Replay Δ** is the meaningful own-delta vs saved base-VLM first shots: prose-after-`print` failures are repaired by stderr-driven local fix without GT.
- **CPU heuristic** injects the same prose-tail fault class to prove loop mechanics when live 8B is unavailable.
- Live `--mlx-eval` on **Studio** (`8e12e5c3…`, user `anthonysanchez`): n=3 base 8B, single=0.000 → loop=1.000, `prompt_touches_gt=false` (~21s). Mac-139 weight blobs incomplete — left GPU for train; Studio used for live generate.
- Oracle = classical CPython. No quantum-advantage claims.

## Anti-contamination

- `prompt_touches_gt=false` on all reported runs.
- Revision prompt fields: task text + PREVIOUS_CODE + EXEC_FEEDBACK(stderr). Harness `expected_stdout` used **only** for post-hoc stdout compare.
- Audit: GT markers + residual check; short tokens (`3` in “Python 3”) excluded as ambiguous.
- Lock: `docs/LOCK-ANTI-CONTAMINATION.md`. Never write `data/lora_adapter/`.

## Artifacts

- `examples/python_verifier_loop.py`
- `data/frontier_python_verifier_cpu_smoke.json`
- `data/frontier_python_verifier_replay_smoke.json`
- `data/frontier_python_verifier_cpu_n16.json`
- `data/frontier_python_verifier_replay_n16.json`
- `data/frontier_python_verifier_mlx_smoke_studio.json` (live 8B Studio)
- `docs/FRONTIER-VERIFIER-PYTHON.md`
