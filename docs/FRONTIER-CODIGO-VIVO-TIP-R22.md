# Frontier — Código-vivo tip hardneg R22

**Branch:** `frontier/tip-hardneg-r22` (side; not folded)  
**Base tip:** `370f35a` (`frontier/codigo-vivo-tip` post tip circ-expand fold freeze/doc sha pin)  
**When:** 2026-09-24T14:59:46-04:00 ET · Mac-111 (`074c6626-…`)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r22`  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`. No CloudAgent.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.
- R7 / R8 / R9 / R10 / R11 / R12 / R13 / label-protect fixtures must still hold after R22 reinforce.
- Do **not** touch tip-cv, tip-tti*, tip-distance-*, tip-hardneg-r12..r21, tip-inverse*, tip-circ*, tip-future*, tip-choose*, tip-pillars*, tip-lp*, tip-label* (other lanes / fold queue). R22 stays side-only. **Do NOT fold.**

## R22 families (≠ R1–R21 / ≠ label-protect)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r22_mixed_router.json` | **52** | sveltekit_hook_gates, remix_loader_gates, nextjs_matcher_gates, nuxt_server_gates, typesense_schema_gates, weaviate_class_gates, milvus_collection_gates, chroma_query_gates, render_health_gates, vercel_cron_gates, netlify_redirect_gates, wasmtime_fuel_gates, wasmer_env_gates, leptos_resource_gates + ent/vision/base controls |
| `data/bench_live/hardneg_r22_python_items.json` | **44** | same coding themes; GT stdout harness-only |

HARD traps (pre-reinforce drops): SvelteKit `gates: handle`; Remix `gates: loader`; Next.js `gates: matcher`; Nuxt `gates: defineEventHandler`; Typesense `gates: token_separators`; Weaviate `gates: vectorizer`; Milvus `gates: index_type`; Chroma `gates: where_document`; Render `gates: healthCheckPath`; Vercel `gates: crons`; Netlify `gates: force`; Wasmtime `gates: fuel`; Wasmer `gates: mapped_dirs`; Leptos `gates: create_resource`; base chat with those distractors + ENT_NEG.

Avoided (R9–R21 + tip-claimed): OpenAPI/Helm/… through Bun/Deno/PocketBase/Appwrite/Neon/PlanetScale/Fly.io/Railway/Meilisearch/Qdrant/Spin/SolidJS/Astro/HTMX and R12–R20 families (Celery/Airbyte/Supabase/Trino/…).

## Scores

| Surface | Pre-reinforce | Post-reinforce (1 layer) |
|---------|---------------|---------------------------|
| R22 router | 6/52 (**0.1154**) | **52/52 (1.0)** |
| R22 verifier alone loop | **1.0** (44/44) | **1.0** (44/44) |
| R22 unified loop | router-limited pre | **1.0** (44/44) |
| Mixed (d) unified overall | **1.0 (held ≥0.967)** | **1.0 (held)** |
| R7–R13 routers | held | **52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52** |
| R12/LP verifiers | held | **44/44 · 32/32** |
| LP router | held | **43/43** |
| Router smoke | 12/12 | 12/12 |
| Pillars / hardneg smoke | 26/26 · 18/18 | held (mixed pillar_routing 29/29 · hardneg 18/18) |
| `ent_never_on_python` | true | true |

Rise: 6→52 hits (**+766%** rate vs pre 0.1154→1.0; **+88.46 pp**) ≥80% freeze gate.

## Reinforce layer (gold-free, once)

1. **Router** — exclude SvelteKit `gates: handle`; Remix `gates: loader`; Next.js `gates: matcher`; Nuxt `gates: defineEventHandler`; Typesense `gates: token_separators`; Weaviate `gates: vectorizer`; Milvus `gates: index_type`; Chroma `gates: where_document`; Render `gates: healthCheckPath`; Vercel `gates: crons`; Netlify `gates: force`; Wasmtime `gates: fuel`; Wasmer `gates: mapped_dirs`; Leptos `gates: create_resource`; hook/loader/matcher/server/schema/class/collection/query/health/cron/redirect/fuel/env/resource prose. R1–R13 patterns unchanged (R14–R21 not on tip base).
2. **Proposer** — none (all 44 heuristic-solvable).

## Freeze polish_r22

| Manifest | pct |
|----------|-----|
| `data/freeze_manifests/tip_moe_verifier_polish_r22_100pct_20260924_145946.json` | **100** |

Evidence: `data/freeze_metrics/codigo_vivo_tip_adv_r22_20260924.json`

## CLI

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r22
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r22_mixed_router.json
.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r22_python_items.json \
  --hardneg-router data/bench_live/hardneg_r22_mixed_router.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `data/bench_live/hardneg_r22_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r22.json`
- `data/frontier_moe_verifier_hardneg_r22.json`
- `data/frontier_moe_verifier_mixed_{cpu,unified}.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r22_20260924.json`
- `data/freeze_manifests/tip_moe_verifier_polish_r22_100pct_20260924_145946.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R22.md` (this file)

## Not folded

Leave tip-cv / tip-tti* / tip-distance-* / tip-hardneg-r12..r21 / tip-inverse* / tip-circ* / tip-future* / tip-choose* / tip-pillars* / tip-lp* / tip-label* alone (fold queue circ→pillars→LP→R14→…→R21). Side branch only. **Do NOT fold.** R22 folds after R21.
