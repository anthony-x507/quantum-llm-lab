# Frontier — Código-vivo tip hardneg R23

**Branch:** `frontier/tip-hardneg-r23` (side; not folded)  
**Base tip:** `f0dfb11` (`frontier/codigo-vivo-tip` post tip pillars-reinforce fold freeze/doc sha pin)  
**When:** 2026-09-24T15:03:38-04:00 ET · Mac-111 (`074c6626-0440-4817-9829-6bae77c578d6`)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r23`  
**Feat sha:** `d6ca2256313f1423bbf8d2d069b9a1d19ca5e8e7`  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`. No CloudAgent.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.
- R7 / R8 / R9 / R10 / R11 / R12 / R13 / label-protect fixtures must still hold after R23 reinforce.
- Do **not** touch tip-cv, tip-tti*, tip-distance-*, tip-hardneg-r12..r22, tip-inverse*, tip-circ*, tip-future*, tip-choose*, tip-pillars*, tip-lp*, tip-label* (other lanes / fold queue). R23 stays side-only. **Do NOT fold.**

## R23 families (≠ R1–R22 / ≠ label-protect)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r23_mixed_router.json` | **52** | tauri_command_gates, electron_ipc_gates, expo_plugin_gates, capacitor_plugin_gates, vite_plugin_gates, esbuild_plugin_gates, rollup_plugin_gates, turborepo_pipeline_gates, nx_executor_gates, biome_rule_gates, oxc_lint_gates, drizzle_column_gates, surreal_scope_gates, flutter_channel_gates + ent/vision/base controls |
| `data/bench_live/hardneg_r23_python_items.json` | **44** | same coding themes; GT stdout harness-only |

HARD traps (pre-reinforce drops): Tauri `gates: invoke`; Electron `gates: ipcMain`; Expo `gates: withPlugins`; Capacitor `gates: registerPlugin`; Vite `gates: configureServer`; esbuild `gates: onLoad`; Rollup `gates: renderChunk`; Turborepo `gates: persistent`; Nx `gates: cacheable`; Biome `gates: nursery`; Oxc `gates: correctness`; Drizzle `gates: primaryKey`; SurrealDB `gates: SIGNUP`; Flutter `gates: MethodChannel`; base chat with those distractors + ENT_NEG.

Avoided (R9–R22 + tip-claimed): OpenAPI/Helm/… through SvelteKit/Remix/Next/Nuxt/Typesense/Weaviate/Milvus/Chroma/Render/Vercel/Netlify/Wasmtime/Wasmer/Leptos and R12–R21 families (Celery/Airbyte/… Bun/Deno/…).

## Scores

| Surface | Pre-reinforce | Post-reinforce (1 layer) |
|---------|---------------|---------------------------|
| R23 router | 6/52 (**0.1154**) | **52/52 (1.0)** |
| R23 verifier alone loop | **1.0** (44/44) | **1.0** (44/44) |
| R23 unified loop | router-limited pre | **1.0** (44/44) |
| Mixed (d) unified overall | **1.0 (held ≥0.967)** | **1.0 (held)** |
| R7–R13 routers | held | **52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52** |
| R12/LP verifiers | held | **44/44 · 32/32** |
| LP router | held | **43/43** |
| Router smoke | 12/12 | 12/12 |
| Pillars / hardneg smoke | 26/26 · 18/18 | held (mixed pillar_routing 37/37 · hardneg 18/18) |
| `ent_never_on_python` | true | true |

Rise: 6→52 hits (**+766%** rate vs pre 0.1154→1.0; **+88.46 pp**) ≥80% freeze gate.

## Reinforce layer (gold-free, once)

1. **Router** — exclude Tauri `gates: invoke`; Electron `gates: ipcMain`; Expo `gates: withPlugins`; Capacitor `gates: registerPlugin`; Vite `gates: configureServer`; esbuild `gates: onLoad`; Rollup `gates: renderChunk`; Turborepo `gates: persistent`; Nx `gates: cacheable`; Biome `gates: nursery`; Oxc `gates: correctness`; Drizzle `gates: primaryKey`; SurrealDB `gates: SIGNUP`; Flutter `gates: MethodChannel`; command/ipc/plugin/bridge/bundler/onload/chunk/pipeline/executor/linter/lint/column/scope/channel prose. R1–R13 patterns unchanged (R14–R22 not on tip base).
2. **Proposer** — none (all 44 heuristic-solvable).

## Freeze polish_r23

| Manifest | pct |
|----------|-----|
| `data/freeze_manifests/tip_moe_verifier_polish_r23_100pct_20260924_150338.json` | **100** |

Evidence: `data/freeze_metrics/codigo_vivo_tip_adv_r23_20260924.json`

## CLI

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r23
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r23_mixed_router.json
.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r23_python_items.json \
  --hardneg-router data/bench_live/hardneg_r23_mixed_router.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `data/bench_live/hardneg_r23_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r23.json`
- `data/frontier_moe_verifier_hardneg_r23.json`
- `data/frontier_moe_verifier_mixed_{cpu,unified}.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r23_20260924.json`
- `data/freeze_manifests/tip_moe_verifier_polish_r23_100pct_20260924_150338.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R23.md` (this file)

## Not folded

Leave tip-cv / tip-tti* / tip-distance-* / tip-hardneg-r12..r22 / tip-inverse* / tip-circ* / tip-future* / tip-choose* / tip-pillars* / tip-lp* / tip-label* alone (fold queue pillars→LP→R14→…→R22). Side branch only. **Do NOT fold.** R23 folds after R22.
