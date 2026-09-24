# Evidence logging — ALWAYS record with visual proof

**Repo:** `quantum-llm-lab` · **Utility:** `examples/evidence_run_logger.py`  
**Policy:** Honest paths only. Never invent metrics. Quantum `data/lora_adapter/` is READ-ONLY.  
**Do not** steal GPU / kill `qlora-*` / `qlab-*` screens / take `TRAIN_LOCK`.

## Goal

Every meaningful eval/run should leave:

1. **Structured JSONL** — timestamp, domain, metrics, inputs, outputs, tool calls, retrieval hits  
2. **Visual frames** when the domain is visual (street lights, balls/rockets, distance, inverse)  
3. **Exportable compare tables** — base vs adapter vs prototype (CSV + Markdown)  
4. **Freeze manifests with git SHA** at ~80% / ~90% / ~100% (Plan Maestro §5.1.B)

---

## What already existed (reuse)

| Sink | Path | Fields / proof |
|------|------|----------------|
| Jev experiment log | `data/experiment_log.jsonl`, `data/experiment_log_v2.jsonl` | `ts`, `scene_id`, `proposal`, `jev_verdict`, `sim_result`, `model_id`, `elapsed_sec` — **no** unified tool/retrieval/frames |
| Domain eval audit | `data/eval_audit/distance_*.jsonl`, `inverse_*.jsonl` | `ts`, `seq_id`, `tool`, `retrieval`, `memory`, `prompt_preview` — written by domain evals |
| Video F1 contamination audit | `data/video_synth/fase1/` (+ `CONTAMINATION_AUDIT.jsonl` via prototype) | anti-contam; frames under each `f1_*/frames/` |
| LoRA compare JSON | `data/eval_compare_{clean,nota_fix,diversity,rebalance}.json` | `base` / `finetuned` / `delta` metrics |
| Hybrid oracle | `data/hybrid_oracle/report.json` | `single_shot`, `after_loop`, `own_delta_base_vs_ours` |
| Night freeze (partial) | `data/lora_adapter_frozen_rebalance_20260924-041300/NIGHT_ADAPTER_FREEZE.json` | metrics + criteria; **no git SHA** in original |
| Night narrative | `data/NIGHT-LOG.md` | human timeline |
| Street-light frames | `data/video_synth/fase1/*/frames/*.png` | 50 seq × 16 frames (3 lights) |
| Distance frames | `data/video_synth/distance_est/*/frames/*.png` | ≥56 seq × 12 frames |
| Balls / rockets frames | `data/classical_scenes/*/frame_*.png` (+ `preview.png`) | baseball/soccer/golf/ballistic/drag_projectile (rockets_projectiles family) |
| Quantum scene frames | `data/scenes/`, `data/experiment_scenes/` | entanglement / fall visuals |

Domain writers (keep using):

- `examples/distance_est/eval_heuristic.py` → `data/eval_audit/distance_<ts>.jsonl`
- `examples/inverse_planning/eval_passive.py` → `data/eval_audit/inverse_<ts>.jsonl`
- `examples/run_jev_experiment.py` → `data/experiment_log*.jsonl`
- `examples/eval_lora.py` → `data/eval_compare_*.json`
- `examples/video_temporal_prototype.py` → fase1 audits + frames

---

## What this utility adds

| Artifact | Path |
|----------|------|
| Unified evidence JSONL | `data/evidence_runs.jsonl` |
| Compare CSV/MD export | `data/compare_tables/<stem>.{csv,md}` |
| Freeze manifests (+ git SHA) | `data/freeze_manifests/<domain>_<pct>pct_<ts>.json` |

### Schema (`SCHEMA_FIELDS`)

```text
ts, run_id, domain, metrics, inputs, outputs,
tool_calls, retrieval_hits, frames, git_sha, notes
```

### CLI

```bash
# Demo (writes one line + exports eval_compare_rebalance if present)
python examples/evidence_run_logger.py demo

# Append a real run (link frames by seq_id when possible)
python examples/evidence_run_logger.py log \
  --domain distance_est \
  --seq-id de_007_ash_ct \
  --metrics '{"overall_correct":0.6529}' \
  --tool-calls '[{"tool":"floor_scale+parallax"}]' \
  --notes "from eval_audit/distance_20260924_045444.jsonl"

# Export base vs adapter vs prototype table
python examples/evidence_run_logger.py export-compare data/eval_compare_rebalance.json

# Freeze an 80/90/100% platform advance WITH git SHA (§5.1.B)
python examples/evidence_run_logger.py freeze \
  --domain quantum_label \
  --pct 90 \
  --metrics-json data/lora_adapter_frozen_rebalance_20260924-041300/NIGHT_ADAPTER_FREEZE.json \
  --artifact data/lora_adapter_frozen_rebalance_20260924-041300 \
  --note "LoRA rebalance label_acc=0.9 platform"
```

Import from other scripts (append-only; never mutates adapters):

```python
from evidence_run_logger import make_record, append_jsonl, find_frames_for_seq, write_freeze_manifest
```

---

## Gaps still requiring design (not a 10-minute install)

1. **Wire-all evals** — domain scripts still write their own JSONL shapes; unifying every writer onto `evidence_runs.jsonl` needs a small API migration per file (do when each domain is next touched).
2. **Eval ↔ frame foreign key** — `eval_audit/distance_*.jsonl` has `seq_id` but not an explicit `frames[]` array; convention is `data/video_synth/distance_est/<seq_id>/frames/`.
3. **Prototype column** — LoRA `eval_compare_*.json` is base/finetuned only; hybrid/amplitude/classical prototypes live in separate reports. `export-compare --prototype '{...}'` is the bridge until a 3-way eval harness exists.
4. **Frozen 80/90/100 git tips as commits** — policy lives in `docs/PLAN-MAESTRO-PARTE-1.md` §5.1.B; historical freezes lacked `git_sha`. New freezes use `data/freeze_manifests/`. Optionally tag `freeze/<domain>-<pct>` later.
5. **Rockets-as-named domain pack** — classical scenes cover `rockets_projectiles` subdomains, but there is no separate `data/video_synth/rockets/` pack; fase2/fase3 street packs are still stubs.

---

## Safety

- Append-only under `data/evidence_runs.jsonl`, `data/compare_tables/`, `data/freeze_manifests/`
- Never overwrite `data/lora_adapter/` or steal GPU
- Stdlib only (no matplotlib required; Pillow already in requirements for scene synth elsewhere)
