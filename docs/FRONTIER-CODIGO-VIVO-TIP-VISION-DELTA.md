# FRONTIER — Código-vivo tip vision own-delta

**Branch:** `frontier/tip-vision-delta` (from tip `3d05cbe`, post collision-n)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-vision-delta` · Mac-111  
**Written:** 2026-09-24 ~13:35 ET  
**Claim scope:** BASE vs OUR RO quantum adapter on vision pillar; dual-lane tip floor. **NO quantum-advantage claims.**  
**Fold into tip:** **NO** (side branch only).

## SHA / setup

| Field | Value |
|-------|-------|
| Tip base SHA | `3d05cbe` (`3d05cbe1ef88eaf3effc2a93049cbb27ba2ef800`) |
| Branch | `frontier/tip-vision-delta` |
| Host | Mac-111 (`074c6626-…`) |
| Adapters | **READ-ONLY** (`ro_mtime_unchanged` on `*.safetensors`) |

### Adapter RO mtimes (ET)

| Adapter | adapters.safetensors mtime | Role on tip |
|---------|---------------------------|-------------|
| `data/lora_adapter/` | 2026-09-24 **00:58** | quantum RO; RAW own-delta; **not** on tip vision |
| `data/lora_adapter_ent2/` | 2026-09-24 **09:02** | MoE **ent** lane |
| `data/lora_adapter_classical/` | 2026-09-24 **05:29** | present; **not** routed on CV pillars |

## Anti-contam

| Check | Result |
|-------|--------|
| `prompt_touches_gt` | **false** |
| CLEAN? | **YES** |
| `ent_never_on_python` | **true** |
| writes to `data/lora_adapter/` | **false** |
| `ro_mtime_unchanged` (safetensors) | **true** |

## Vision BASE vs adapter (RAW own-delta)

Prior lock (unchanged source): `data/BENCHMARK_CODIGO_VIVO.json`

| | base | adapter (quantum RO) | Δ |
|--|------|----------------------|---|
| Vision accuracy | **0.900** (9/10) | **0.700** (7/10) | **−0.200** |

### Adapter fails (why Δ is negative)

| id | cause | parse-polish rescues? |
|----|-------|----------------------|
| `vis_math_06` | last-int extract picked `24` from sequence; JSON had `"next_term": "48"` | **YES** |
| `vis_circ_01` | content missing **X** (emitted H+CX only) | **NO** |
| `vis_circ_02` | wrong gates (H+RY vs RY+Z); also bare `pi/2` JSON | parse only (content still wrong) |

Base sole miss: `vis_circ_02` narrative parse — tip mixed path already gold-free-reparses → scored vis **1.0**.

## Parse polish (non-adapter) on this branch

1. `examples/bench_codigo_vivo.py` — `_extract_int_answer` prefers JSON keys `next_term` / `answer` / `result` / … before last-int.  
2. `examples/llm_quantum_bridge.py` — `_sanitize_jsonish` + `parsear_propuesta` tolerate bare `pi/2` / `π`.  
3. `examples/moe_verifier_mixed_live.py` — same pi sanitize in `gold_free_extract_json_obj`.

**Expected if RAW vision rebenched with polish (adapters still RO, no retrain):**  
adapter **0.8** (math_06 rescued) · base **0.9** · Δ **−0.1**.  
Full MLX rebench **not** re-run this side-branch (tip keeps BASE for vis; cost/noise). Offline probe confirmed `next_term→48` and `pi/2` parse.

## Honest ceiling

| Question | Answer |
|----------|--------|
| Non-negative vision own-delta with current quantum RO? | **NO** |
| Parse-only ceiling | ≈ **−0.1** (still negative) |
| Irreducible without new vision LoRA | `vis_circ_01` missing X; `vis_circ_02` wrong gate set |
| Tip policy | **Keep vision on BASE** (dual-lane). Never put quantum LoRA on vis while Δ\<0. |

### Next reinforce angles (do **not** write `data/lora_adapter/`)

- Train a **vision-specific** LoRA under a **new** directory; score own-delta separately.  
- Circuit grounding prompt: require explicit **X** when diagram shows Pauli-X before CX.  
- Reuse anti-think JSON-only cue (`vision/grounding.py`) on bench vision circuit items.  
- Hold tip vision on BASE until a dedicated adapter shows own-delta ≥ 0.

## Tip mixed floor (held)

CPU smoke + cpu-eval @ this branch:

| Path | python | ent | vision | overall |
|------|--------|-----|--------|---------|
| (a) baseline | 0.000 | 0.000 | 1.000 | 0.333 |
| (b) MoE alone | 0.000 | **1.000** | 1.000 | 0.667 |
| (c) verifier-on-python | **1.000** | 0.000 | 1.000 | 0.667 |
| (d) unified | **1.000** | **1.000** | **1.000** | **1.000** |

pillars **26/26** · hardneg **18/18** · `ent_never_on_python` · freezes retained (collision_n / motion_r2 / distance / collision_pred / r8 / scaffold + priors).

## Freeze?

**NO.** Criterion was ≥80% held **AND** rise. Floor held at unified **1.0**, but vision own-delta remains negative (honest ceiling ≈ −0.1); tip vis already 1.0 — no freeze-bar rise. Document ceiling instead.

## Reproduce

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-vision-delta
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
# RO symlinks: data/lora_adapter{,_ent2,_classical} → lab data (never write)
.venv/bin/python examples/moe_verifier_mixed_live.py --smoke \
  --out data/frontier_moe_verifier_mixed_smoke_vision_delta.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval \
  --out data/frontier_moe_verifier_mixed_cpu_vision_delta.json
```

## Artifacts

- `data/frontier_tip_vision_delta_scoreboard.json` (SSOT)
- `data/frontier_moe_verifier_mixed_smoke_vision_delta.json`
- `data/frontier_moe_verifier_mixed_cpu_vision_delta.json`
- `data/tip_vision_delta_adapter_ro_snapshot_{before,after}.json`
- Prior RAW: `data/BENCHMARK_CODIGO_VIVO.json`
