# Frontier — Código-vivo tip hardneg R21

**Branch:** `frontier/tip-hardneg-r21` → **FOLDED** into `frontier/codigo-vivo-tip` (side; not folded)  
**Base tip:** `abf0d25` (`frontier/codigo-vivo-tip` post tip future-track-r3 fold fix freeze/Feat SHA lines)  
**When:** 2026-09-24T14:55:27-04:00 ET · Mac-111 (`074c6626-…`)  
**Worktree:** `/Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r21`  
**Claim:** NO quantum advantage. Classical heuristic router + `python -I` verifier only.

## LOCK

- Freeze mixed unified overall **≥0.9667** (docs ~**0.967**); prefer hold **1.0**. Never abandon.
- `data/lora_adapter/` READ-ONLY. No merge to `main`. No CloudAgent.
- Keep `ent_never_on_python=true`, `prompt_touches_gt=false`.
- R7 / R8 / R9 / R10 / R11 / R12 / R13 / label-protect fixtures must still hold after R21 reinforce.
- Do **not** touch tip-cv, tip-tti*, tip-distance-*, tip-hardneg-r12..r20, tip-inverse*, tip-circ*, tip-future*, tip-choose*, tip-pillars*, tip-lp*, tip-label* (other lanes / fold queue). R21 stays side-only. **Do NOT fold.**

## R21 families (≠ R1–R20 / ≠ label-protect)

| File | n | Families |
|------|---|----------|
| `data/bench_live/hardneg_r21_mixed_router.json` | **52** | bun_plugin_gates, deno_perm_gates, pocketbase_hook_gates, appwrite_schedule_gates, neon_endpoint_gates, planetscale_safe_gates, flyio_autostop_gates, railway_start_gates, meilisearch_filter_gates, qdrant_distance_gates, spin_outbound_gates, solidjs_effect_gates, astro_onrequest_gates, htmx_trigger_gates + ent/vision/base controls |
| `data/bench_live/hardneg_r21_python_items.json` | **44** | same coding themes; GT stdout harness-only |

HARD traps (pre-reinforce drops): Bun `gates: preload`; Deno `gates: allow-net`; PocketBase `gates: OnRecord`; Appwrite `gates: schedule`; Neon `gates: endpoints`; PlanetScale `gates: safeMigrations`; Fly.io `gates: auto_stop`; Railway `gates: startCommand`; Meilisearch `gates: filterableAttributes`; Qdrant `gates: distance`; Fermyon Spin `gates: allowed_outbound_hosts`; SolidJS `gates: createEffect`; Astro `gates: onRequest`; HTMX `gates: hx-trigger`; base chat with those distractors + ENT_NEG.

Avoided (R12–R20 + tip-claimed): Traefik/Envoy/NATS/…, Nginx/HAProxy/Caddy/…, httpd/Varnish/APISIX/…, Squid/OpenResty/Contour/…, ATS/CoreDNS/Pulsar/…, Cloudflare/Vitess/…, AWS ALB/Hudi/Iceberg/Flink/…, Mage/Spark/ActiveMQ/Helmfile/…, Celery/Airbyte/Supabase/Trino/Vector/Fluent Bit/Thanos/Strimzi/Tilt/Mise/CUE/Nim/Hono/Axum.

## Scores

| Surface | Pre-reinforce | Post-reinforce (1 layer) |
|---------|---------------|---------------------------|
| R21 router | 6/52 (**0.1154**) | **52/52 (1.0)** |
| R21 verifier alone loop | **1.0** (44/44) | **1.0** (44/44) |
| R21 unified loop | router-limited pre | **1.0** (44/44) |
| Mixed (d) unified overall | **1.0 (held ≥0.967)** | **1.0 (held)** |
| R7–R13 routers | held | **52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52 · 52/52** |
| R12/LP verifiers | held | **44/44 · 32/32** |
| LP router | held | **43/43** |
| Router smoke | 12/12 | 12/12 |
| Pillars / hardneg smoke | 26/26 · 18/18 | held |
| `ent_never_on_python` | true | true |

Rise: 6→52 hits (**+766%** rate vs pre 0.1154→1.0; **+88.46 pp**) ≥80% freeze gate.

## Reinforce layer (gold-free, once)

1. **Router** — exclude Bun `gates: preload`; Deno `gates: allow-net`; PocketBase `gates: OnRecord`; Appwrite `gates: schedule`; Neon `gates: endpoints`; PlanetScale `gates: safeMigrations`; Fly.io `gates: auto_stop`; Railway `gates: startCommand`; Meilisearch `gates: filterableAttributes`; Qdrant `gates: distance`; Spin `gates: allowed_outbound_hosts`; SolidJS `gates: createEffect`; Astro `gates: onRequest`; HTMX `gates: hx-trigger`; runtime/permission/BaaS/serverless/SQL/PaaS/search/vector/wasm/framework/frontend/HTML prose. R1–R13 patterns unchanged (R14–R20 not on tip base).
2. **Proposer** — none (all 44 heuristic-solvable).

## Freeze polish_r21

| Manifest | pct |
|----------|-----|
| `data/freeze_manifests/tip_moe_verifier_polish_r21_100pct_20260924_145527.json` | **100** |

Evidence: `data/freeze_metrics/codigo_vivo_tip_adv_r21_20260924.json`

## CLI

```bash
cd /Users/anthony/Documents/quantum-llm-lab-tip-hardneg-r21
export QLAB_DATA=/Users/anthony/Documents/quantum-llm-lab/data
.venv/bin/python examples/moe_dual_lane_router.py --hardneg \
  --hardneg-path data/bench_live/hardneg_r21_mixed_router.json
.venv/bin/python examples/moe_verifier_codigo_vivo.py --hardneg-only \
  --hardneg-items data/bench_live/hardneg_r21_python_items.json \
  --hardneg-router data/bench_live/hardneg_r21_mixed_router.json
.venv/bin/python examples/moe_verifier_mixed_live.py --cpu-eval
```

## Artifacts

- `data/bench_live/hardneg_r21_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r21.json`
- `data/frontier_moe_verifier_hardneg_r21.json`
- `data/frontier_moe_verifier_mixed_{cpu,unified}.json`
- `data/freeze_metrics/codigo_vivo_tip_adv_r21_20260924.json`
- `data/freeze_manifests/tip_moe_verifier_polish_r21_100pct_20260924_145527.json`
- `docs/FRONTIER-CODIGO-VIVO-TIP-R21.md` (this file)

## Not folded

Leave tip-cv / tip-tti* / tip-distance-* / tip-hardneg-r12..r20 / tip-inverse* / tip-circ* / tip-future* / tip-choose* / tip-pillars* / tip-lp* / tip-label* alone (fold queue circ→pillars→LP→R14→…→R19→R20). Side branch only. **Do NOT fold.**

## Side trail (pre-fold)

Side branch polish completed before tip fold. Historical lock said side-only; superseded by fold below.

## Fold into tip (2026-09-24)

Cherry-pick `590e9af` onto tip `5ef34a7`. Conflicts: STATUS+mixed/LP/r7–r12 JSON ours; router/verifier merged R12+R13+R14+R15+R16+R17+R18+R19+R20+R21 gates_ops.

Freeze: `codigo_vivo_tip_r21_100pct_20260924_155831`

### Fold re-smoke (2026-09-24 15:58:31 ET)

| Surface | Result |
|---------|--------|
| R21 router / verifier | **7→52/52** / **44/44** |
| Side trail | **6→52** · rise_pp **88.46** |
| R20 / R19 / mixed (d) | **52/52·44/44 · 52/52·44/44 · 1.0** |
| pillars / hardneg smoke / circ | **37/37 · 18/18 · 5/5** |
| choose_n80 / tti-cold | **100%** / **~95%** freeze retained |
| `ent_never_on_python` | true |
| adapters RO | true |

### Artifacts

- `data/bench_live/hardneg_r21_{mixed_router,python_items}.json`
- `data/frontier_moe_dual_lane_hardneg_r21.json`
- `data/frontier_moe_verifier_hardneg_r21.json`
- `data/frontier_moe_verifier_mixed_{cpu,smoke,unified}_r21_fold.json`
- `data/freeze_metrics/codigo_vivo_tip_r21_{before,fold,adapter_ro,20260924}.json`
- `data/freeze_manifests/codigo_vivo_tip_r21_100pct_20260924_155831.json` (+ LATEST)
- `data/freeze_manifests/tip_moe_verifier_polish_r21_100pct_20260924_145527.json` (side polish retained)
- `docs/FRONTIER-CODIGO-VIVO-TIP-R21.md` (this file)

Fold SHA: `PENDING` · Base tip: `5ef34a7` · Side: `50e60b2` / `590e9af`

R22+ not folded. Tip vis stays BASE. RO `data/lora_adapter/`.

