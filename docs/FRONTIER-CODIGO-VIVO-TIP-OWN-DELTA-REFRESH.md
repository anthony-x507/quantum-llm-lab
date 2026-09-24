# FRONTIER — Código-vivo tip own-delta refresh

**Branch:** `frontier/tip-own-delta-refresh` (from tip `3b10288`)  
**Written:** 2026-09-24 ~12:50 ET · Mac-111 (`074c6626-…`)  
**Claim scope:** BASE vs OUR RO adapters on tip MoE+verifier dual-lane **after label-protect freeze**. **NO quantum-advantage claims.**

## SHA / setup

| Field | Value |
|-------|-------|
| Tip base SHA | `3b10288` (`3b10288cc568255f7782640d7344078c441ad506`) |
| Branch | `frontier/tip-own-delta-refresh` |
| Host | Mac-111 |
| Adapters | **READ-ONLY** (`ro_mtime_unchanged=true`) |

### Adapter RO mtimes (ET)

| Adapter | adapters.safetensors mtime | Role on tip |
|---------|---------------------------|-------------|
| `data/lora_adapter/` | 2026-09-24 **00:58** | quantum RO; RAW own-delta source |
| `data/lora_adapter_ent2/` | 2026-09-24 **09:02** | MoE **ent** lane |
| `data/lora_adapter_classical/` | 2026-09-24 **05:29** | present; **not** routed on CV pillars |

## Anti-contam

| Check | Result |
|-------|--------|
| `prompt_touches_gt` | **false** |
| CLEAN? | **YES** |
| `ent_never_on_python` | **true** |
| scaffold `gt_leak` | **0** |
| writes to `data/lora_adapter/` | **false** |
| `ro_mtime_unchanged` | **true** |

## Pillar table — base | adapter | Δ

### A) Prior RAW own-delta (quantum `lora_adapter`, 05:00 ET) — unchanged

| pillar | metric | base | adapter (quantum RO) | Δ |
|--------|--------|------|----------------------|---|
| Python | solve_rate | **0.062** (1/16) | **0.000** (0/16) | **−0.062** |
| Entanglement | label_acc | **0.000** (0/12) | **1.000** (12/12) | **+1.000** |
| Vision | accuracy | **0.900** (9/10) | **0.700** (7/10) | **−0.200** |

### B) Tip dual-lane @ `3b10288` (label-protect + R5 + wired_to_vlm)

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

Δ MoE vs baseline: ent **+1.0**, overall **+0.3334** (visible). **Floor held.**

### D) Tip MLX sample (honest n: py2 / ent3 / vis2)

| Path | python | ent | vision | overall |
|------|--------|-----|--------|---------|
| (d) unified | **1.000** | **1.000** | **1.000** | **1.000** |

vs CPU overall 1.0: **Δ=0**. drops: **none**.  
Ent live own-delta: BASE label **0.0** (0/3) → ent2 **1.0** (3/3); `wired_to_vlm=true` (`text_scaffold_prefix`).

## Freezes cited (retained)

- `codigo_vivo_tip_platform_100pct_20260924_111435`
- `codigo_vivo_tip_mlx_r3_100pct_20260924_112131`
- `codigo_vivo_tip_post_polish_100pct_20260924_123210`
- `codigo_vivo_tip_r5_100pct_20260924_123727`
- `codigo_vivo_tip_label_protect_100pct_20260924_124608`

## Honesty / blockers

- Tip stack still **needs** ent2 for ent (+1.0); **must not** put quantum adapter on py/vis (RAW −0.062 / −0.200).
- Label-protect dual-lane reinforce does **not** change RAW adapter deltas; it keeps tip floor **1.0**.
- **Blockers:** none.

## Reproduce

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-own-delta-r2
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
# RO symlinks: data/lora_adapter{,_ent2,_classical} + data/scenes → lab (never write)
.venv/bin/python examples/moe_verifier_mixed_live.py --smoke \
  --out data/frontier_moe_verifier_mixed_smoke_own_delta_refresh.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval \
  --out data/frontier_moe_verifier_mixed_cpu_own_delta_refresh.json
.venv/bin/python examples/moe_verifier_mixed_mlx_live_pillars.py \
  --n-py 2 --n-ent 3 --n-vis 2 --rounds 2 \
  --out data/frontier_tip_own_delta_refresh_mlx_sample.json
```

## Artifacts

- `data/frontier_tip_own_delta_refresh_scoreboard.json`
- `data/frontier_moe_verifier_mixed_smoke_own_delta_refresh.json`
- `data/frontier_moe_verifier_mixed_cpu_own_delta_refresh.json`
- `data/frontier_tip_own_delta_refresh_mlx_sample.json`
- `data/tip_own_delta_refresh_adapter_ro_snapshot_{before,after}.json`
