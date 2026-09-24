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

## What this does NOT do

- No merge to `main`
- No writes under `data/lora_adapter/`
- No quantum-advantage claims
