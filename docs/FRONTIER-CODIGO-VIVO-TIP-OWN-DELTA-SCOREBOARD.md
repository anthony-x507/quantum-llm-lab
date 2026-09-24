# FRONTIER — Código-vivo tip own-delta scoreboard

**Branch:** `frontier/tip-own-delta-scoreboard` → **FOLDED** into `frontier/codigo-vivo-tip` (from tip `459f6da`, rebase onto `0a1ef4d`)  
**Written:** 2026-09-24 12:27:42 ET · Mac-111 (`074c6626-…`)  
**Claim scope:** BASE vs OUR RO adapters on tip MoE+verifier dual-lane. **NO quantum-advantage claims.**

## SHA / setup

| Field | Value |
|-------|-------|
| Tip base SHA | `459f6da` (`459f6da9fe6ed99e26ac8d8f46f67f008a8b5328`) |
| Branch | `frontier/tip-own-delta-scoreboard` (separate; tip may be fold-busy) |
| Host | Mac-111 |
| Adapters | **READ-ONLY** (mtime unchanged after run) |

### Adapter RO mtimes (ET)

| Adapter | adapters.safetensors mtime | Role on tip |
|---------|---------------------------|-------------|
| `data/lora_adapter/` | 2026-09-24 **00:58** | quantum RO; RAW own-delta source |
| `data/lora_adapter_ent2/` | 2026-09-24 **09:02** (dir **10:13**) | MoE **ent** lane |
| `data/lora_adapter_classical/` | 2026-09-24 **05:29** | present; **not** routed on CV pillars |

`ro_mtime_unchanged=true` (before/after snapshots in JSON).

## Anti-contam

| Check | Result |
|-------|--------|
| `prompt_touches_gt` | **false** |
| CLEAN? | **YES** |
| `ent_never_on_python` | **true** |
| scaffold `gt_leak` | **0** |
| writes to `data/lora_adapter/` | **false** |

## Pillar table — base | adapter | Δ

### A) Prior RAW own-delta (quantum `lora_adapter`, 05:00 ET)

Same numbers as prior lock (Py −0.062, Ent +1.0, Vision −0.200); anti-contam CLEAN.

| pillar | metric | base | adapter (quantum RO) | Δ |
|--------|--------|------|----------------------|---|
| Python | solve_rate | **0.062** (1/16) | **0.000** (0/16) | **−0.062** |
| Entanglement | label_acc | **0.000** (0/12) | **1.000** (12/12) | **+1.000** |
| Vision | accuracy | **0.900** (9/10) | **0.700** (7/10) | **−0.200** |

### B) Tip dual-lane (MoE routes correctly) — do adapters still help/hurt?

| pillar | tip uses | tip rate (CPU d / MLX sample) | adapter still helps? |
|--------|----------|-------------------------------|----------------------|
| Python | BASE + verifier (no LoRA) | **1.000** / loop **1.000** (n=2) | **No** — quantum LoRA hurts; tip avoids it |
| Entanglement | **ent2** RO + scaffold wire | **1.000** / **1.000** (n=3, 0→3) | **Yes** — ent2 Δ **+1.0** vs BASE |
| Vision | BASE (no LoRA) | **1.000** / **1.000** (n=2) | **No** — quantum LoRA hurts (−0.200); tip uses BASE |

### C) Tip CPU paths (a)(b)(c)(d)

| Path | python | ent | vision | overall |
|------|--------|-----|--------|---------|
| (a) baseline | 0.000 | 0.000 | 1.000 | 0.333 |
| (b) MoE alone | 0.000 | **1.000** | 1.000 | 0.667 |
| (c) verifier-on-python | **1.000** | 0.000 | 1.000 | 0.667 |
| (d) unified | **1.000** | **1.000** | **1.000** | **1.000** |

Δ MoE vs baseline: ent **+1.0**, overall **+0.3334** (visible).

### D) Tip MLX sample (honest n: py2 / ent3 / vis2)

| Path | python | ent | vision | overall |
|------|--------|-----|--------|---------|
| (a) baseline | 0.000 | 0.000 | 1.000 | 0.333 |
| (b) MoE alone | 0.000 | **1.000** | 1.000 | 0.667 |
| (c) verifier-on-python | **1.000** | 0.000 | 1.000 | 0.667 |
| (d) unified | **1.000** | **1.000** | **1.000** | **1.000** |

vs CPU overall 1.0: **Δ=0**. drops: **none**. elapsed ~104s.

Ent live own-delta: BASE label **0.0** (0/3) → ent2 **1.0** (3/3); `wired_to_vlm=true` (`text_scaffold_prefix`).

## Classical

Present at `data/lora_adapter_classical/` (mtime 05:29 ET). **Not** selected by tip MoE for código-vivo python/ent/vision lanes. No classical→CV transfer scoreboard this run (out of scope for dual-lane honesty).

## Smoke

pillars **26/26** · hardneg **18/18** · scaffold injected **10** · `wired_to_vlm=true`

## Honesty / blockers

- Tip stack (MoE+verifier unified 1.0) **still needs** ent2 for ent (+1.0); **must not** put quantum adapter on py/vis (RAW −0.062 / −0.200).
- Dual-lane routing is the mechanism that keeps tip at 1.0 while adapters remain specialized.
- **Blockers:** none.

## Reproduce

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-own-delta-scoreboard
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
# RO symlinks: data/lora_adapter{,_ent2,_classical} → lab data (never write)
.venv/bin/python examples/moe_verifier_mixed_live.py --smoke \
  --out data/frontier_moe_verifier_mixed_smoke_own_delta.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval \
  --out data/frontier_moe_verifier_mixed_cpu_own_delta.json
.venv/bin/python examples/moe_verifier_mixed_mlx_live_pillars.py \
  --n-py 2 --n-ent 3 --n-vis 2 --rounds 2 \
  --out data/frontier_tip_own_delta_mlx_sample.json
```

## Artifacts

- `data/frontier_tip_own_delta_scoreboard.json` (this run SSOT)
- `data/frontier_moe_verifier_mixed_smoke_own_delta.json`
- `data/frontier_moe_verifier_mixed_cpu_own_delta.json`
- `data/frontier_tip_own_delta_mlx_sample.json` (+ `.log`)
- `data/tip_own_delta_adapter_ro_snapshot_{before,after}.json`
- Prior RAW: `data/BENCHMARK_CODIGO_VIVO.json`


## FOLDED into tip

**When:** 2026-09-24 12:31:44 ET · Mac-111 (`074c6626-…`)  
**Method:** rebase `2382c90` (parent `459f6da`) onto tip `0a1ef4d` → `66db30a` FF into `frontier/codigo-vivo-tip`.  
**Conflicts:** `STATUS.md` (keep both sections); `mixed_unified.json` (ours/tip; re-smoke). Scoreboard auto-merged own-delta table.  
**CPU re-smoke:** unified overall **1.0** (py/ent/vis 1.0); hardneg R1–R4 **18/18·22/22·35/35·40/40**; R3/R4 verifier **28/28·32/32**; `wired_to_vlm=true`.  
**Honesty held:** RAW Py **−0.062** / Ent **+1.0** / Vis **−0.200**; dual-lane protects tip at 1.0 (ent2 helps; quantum alone hurts py/vis).  
**Freezes:** platform / mlx_r3 / polish_r4 **retained**; new `codigo_vivo_tip_post_polish_100pct_20260924_123210` cites tip HEAD `bf58743`.  
**RO:** no `lora_adapter` writes. No `main` merge. Anti-contam **CLEAN**.

**Reproduce (CPU floor):**
```bash
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_verifier_mixed_live.py --smoke
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```
