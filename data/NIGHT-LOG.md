
## 2026-09-24 04:39:22 EDT — QLab night tip-of-spear checkpoint
- Train healthy: Iter 730/1140 loss≈92 rate≈0.495 ETA≈13.8m (qlora-ent)
- Waiter qlab-after-ent still polling for TRAIN_DONE then pillars+ent-eval
- Code enrich: +4 bell (zhcx,hycx,ryhcx,hcx_x) +4 sep (xy,hz,yz,ryx) in train_lora.py + synthetic_physics_dataset.py
- Scenes +80 ent (0380–0459); staged data/lora_dataset_ent_v2.jsonl = 460 rows
- Live hf dataset untouched; classical smoke yielding GPU
- Silent to Anthony (morning 08:19 reports)

- 2026-09-24 04:44:29 EDT — **agent_layers executor: REDUNDANT w/ video F1.** Canonical 3-layers+anti-contam+--ablate already in `examples/video_temporal_prototype.py` (99867ae) + `data/video_synth/fase1/`. Did NOT rebuild street set; removed draft `synthetic_street_f1.py` / mini_layers fork. `examples/agent_layers/README.md` → pointer. Doc: `docs/THREE-LAYERS-PROTOTYPE.md`. Ablation table pending GPU (`qlora-video-f1`). No GPU stolen; `data/lora_adapter/` untouched. Inverse-planning left to other executor.

- 2026-09-24 04:54:56 EDT — **distance-est executor (FLOOR-SCALE):** ≥56 seq under `data/video_synth/distance_est/` with GT meters in `distances_gt.json` only. Scale lock = building floors 2.4–3.0 m — **NO fixed object heights** (lights vary 3–5 m). CPU heuristic eval CLEAN: overall **65.29%** correct by range (~5m 76.3 / ~50m 48.7 / ~100m 76.7 / ~200m 56.7). Tracking±distance both ~100% (easy synth). Future depth-pred: tracking-only 73.5% vs +distance 64.2% (hold-last wins on heuristic; honest). Audit `data/eval_audit/distance_*.jsonl`. Docs: `docs/LOCK-DISTANCE-EST.md` + `docs/DISTANCE-EST-F1.md`. Adapter dir `data/lora_adapter_distance/` empty; GPU LoRA staged not stolen. Quantum `data/lora_adapter/` mtime untouched. Screens preserved (no kill).
