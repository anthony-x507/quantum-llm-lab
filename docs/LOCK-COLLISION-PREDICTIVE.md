# LOCK — Predictive collision layer (Anthony ~05:05 ET 2026-09-24)

**Separate domain** — top-down merge lane; do not fork street-lights F1 set.
Quantum `data/lora_adapter/` = READ-ONLY. No quantum-advantage claims.

## Task
At frame N, under a **hypothetical action** (coast / brake / accelerate /
turn_left / turn_right), predict physical **consequence** at N+k using
elastic disk collision physics (trajectories, velocities, **masses**).

Emit schema (required):
- `chosen_action`
- `predicted_consequence`
- `is_safe` (bool)

GT = real future under that action (`consequences_gt.json` sidecar) —
**post-hoc only**.

## Metrics
- % correct collision predictions (is_safe + consequence family) vs GT
- Breakdown by horizon k = 1, 3, 5
- **Ablation:** collision physics layer vs inverse-style CV (no masses /
  no collision resolution) on the same action-conditional queries

## Anti-contamination
1. Consequence / future GT **never** in prompt, WorkingMemory, or retrieval.
2. Retrieval index = train ids only; leak → INVALID discard.
3. Audit JSONL every eval step; dirty inject → INVALID.
4. Tools = real NumPy elastic sim — never answer keys.

## Paths
- Code: `examples/collision_predictive/`
- Data: `data/collision_predictive/`
- Adapter (later): `data/lora_adapter_collision/` only
- Audit: `data/eval_audit/collision_*.jsonl`

## Integration notes
- WorkingMemory: `memory_bridge.emit_to_tool_out` (refuses `gt_*`)
- Inverse F1: action-conditional = Fase 2 sketch; pos CV floor stays in
  `data/inverse_planning/` — compare tables only
- Distance: floor-scale band may cue urgency (`distance_note`); VLM deferred

## GPU
CPU physics + synth GT OK now. Do **not** kill screens
`qlora-classical`, `qlora-video-f1`, `qlab-after-ent`, `qlab-ent-v2-wait`,
`qlab-enrich-plan`. No GPU steal.


## n-expand (2026-09-24 tip-collision-n)

Side branch `frontier/tip-collision-n` @ tip `763fb8c` scales eval **8 → 40** seqs
(**555 → 2850** queries), seed `24092446`, split 160/40. Physics oracle must stay
≥80% (held **100%**). See `docs/FRONTIER-CODIGO-VIVO-TIP-COLLISION-N.md`.
