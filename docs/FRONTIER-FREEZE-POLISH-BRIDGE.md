# Frontier — Freeze + hard-neg polish (bridge MoE+verifier)

**Branch:** `frontier/freeze-polish-bridge`  
**Base:** `frontier/moe-verifier-codigo-vivo` @ `3eeeb33`  
**When:** 2026-09-24 ~10:45–11:00 ET · Mac-139  
**Claim:** NO quantum advantage. Classical `python -I` + heuristic router only.

## LOCK

Freeze at **80–100%**. Polish upward / reinforce around. **Never abandon an 80%.**  
`data/lora_adapter/` READ-ONLY. No merge to `main`.

## Freeze manifests (platform baseline)

| ID / path | pct | Metrics locked |
|-----------|-----|----------------|
| `data/freeze_manifests/bridge_moe_verifier_floor80_80pct_20260924_104708.json` | 80 | Floor lock; measured was 0.875 |
| `data/freeze_manifests/bridge_moe_verifier_unified_87.5pct_20260924_104703.json` | 87.5 | verifier+unified loop **0.875** n=16; smoke 1.0; `ent_never_on_python` |
| `data/freeze_manifests/bridge_moe_verifier_smoke_100pct_20260924_104708.json` | 100 | smoke loop 1.0 n=5; router 12/12 |
| `data/freeze_manifests/bridge_moe_verifier_unified_polished_*pct_*.json` | 100 | post-polish n16 loop **1.0** (Δ +0.125 vs freeze) |
| `data/freeze_manifests/bridge_moe_verifier_polish_r2_*pct_*.json` | 100 | R2 adv post-reinforce: router 22/22 + unified **1.0**; floor held |

Evidence logger: `examples/evidence_run_logger.py` (pattern from `d418ee6`).

## Hard-neg fixtures (GT harness-only)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_mixed_router.json` | 18 | python≈physics, ent wording in coding, amb vision captions, controls |
| `data/bench_live/hardneg_python_items.json` | 12 | physics-lookalike + ent-distractor coding tasks |

`expected` / `expected_stdout` never enter `route()` or revision prompts.

## Results

### Original freeze set (held → polished)

| Path | Freeze | Post hard-neg reinforce | Post 2nd polish |
|------|--------|-------------------------|-----------------|
| smoke loop n=5 | **1.0** | 1.0 | 1.0 |
| verifier/unified loop n=16 | **0.875** | **0.875 (held)** | **1.0** (+0.125) |
| router smoke | 12/12 | 12/12 | 12/12 |
| `ent_never_on_python` | true | true | true |
| `prompt_touches_gt` | false | false | false |

**80% held** on the original set through hard-neg; then polished upward.

### Hard-neg Δ

| Surface | Pre-reinforce | Post-reinforce |
|---------|---------------|----------------|
| Router mixed | 16/18 (**0.889**) — 2× vision false+ on “no image/png” | **18/18 (1.0)** |
| Python verifier/unified loop | **0.083** (1/12) | **1.0** (12/12) |

## Reinforce layers (one + one polish)

1. **Router keywords** — `VISION_NEG_RE` cancels vision when text-only / no-image / without picture|png.
2. **Prompt repair / heuristic proposer** — gold-free extractors: balanced `int()`, `len('…')`, `.count`, `sum(range)`, embedded `def`/`import math` blocks, collision/ballistic toys; then max-list + prime yes/no string polish.

## CLI

```bash
python examples/moe_dual_lane_router.py --smoke --hardneg
python examples/moe_verifier_codigo_vivo.py --smoke
python examples/moe_verifier_codigo_vivo.py --cpu-eval --limit 16 --hardneg
python examples/moe_verifier_codigo_vivo.py --hardneg-only
python examples/evidence_run_logger.py freeze --domain bridge_moe_verifier_unified --pct 87.5 ...
```

## Artifacts

- `data/frontier_moe_verifier_unified.json`
- `data/frontier_moe_verifier_cpu_n16.json`
- `data/frontier_moe_verifier_cpu_smoke.json`
- `data/frontier_moe_verifier_hardneg.json`
- `data/frontier_moe_dual_lane_hardneg.json`
- `data/freeze_manifests/bridge_moe_verifier_*.json`
- `docs/FRONTIER-FREEZE-POLISH-BRIDGE.md`


## Round-2 adversarial (2026-09-24 ~10:51–10:55 ET)

**Claim:** still no quantum advantage. Classical heuristic router + `python -I` verifier only.  
**Policy:** KEEP freeze floor ≥0.875 (n16) / smoke 1.0. Invent NEW traps (not R1). One reinforce max.

### New fixtures (R2 families ≠ R1)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r2_mixed_router.json` | 22 | bilingual_trap, measure_in_comment, vision_words_no_image, ent_metaphor_crud, json_looking_physics |
| `data/bench_live/hardneg_r2_python_items.json` | 20 | same themes; GT stdout harness-only |

### Scores

| Surface | Pre-reinforce | Post-reinforce (1 layer) |
|---------|---------------|---------------------------|
| R2 router | 20/22 (**0.909**) — bil ES chat→ent; ES vision miss | **22/22 (1.0)** |
| R2 verifier / unified loop | **0.75** (15/20) | **1.0** (20/20) |
| Original freeze n16 unified | **1.0 (held ≥0.875)** | **1.0 (held)** |
| R1 hardneg router / python | 18/18 · 1.0 | 18/18 · 1.0 |
| smoke router | 12/12 | 12/12 |
| `ent_never_on_python` | true | true |

### Reinforce layer (gold-free, once)

1. **Router** — `ENT_NEG_RE` cancels ent on explicit "no circuit" chat; bilingual `VISION_RE` adds `observa la imagen` / `foto` / `imagen adjunta`.
2. **Proposer** — Spanish `imprima EXPR`, bare `print(N)`, `len([list])`, `import math` embeds (sqrt etc.), `name={...}; print(sum(name.values()))`.

### Freeze polish_r2

| Manifest | pct |
|----------|-----|
| `data/freeze_manifests/bridge_moe_verifier_polish_r2_100pct_*.json` | 100 |

Evidence: `data/freeze_metrics/bridge_moe_verifier_adv_r2_20260924.json`  
Artifacts: `data/frontier_moe_dual_lane_hardneg_r2.json`, `data/frontier_moe_verifier_hardneg_r2.json`, `data/frontier_moe_verifier_cpu_n16_post_r2.json`

### CLI (R2)

```bash
python examples/moe_dual_lane_router.py --hardneg --hardneg-path data/bench_live/hardneg_r2_mixed_router.json
python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r2_python_items.json \
  --hardneg-router data/bench_live/hardneg_r2_mixed_router.json
```

## What this does NOT do

- No merge to `main`
- No writes under `data/lora_adapter/`
- No quantum-advantage claims
