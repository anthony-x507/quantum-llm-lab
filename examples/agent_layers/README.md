# agent_layers — POINTER (do not fork)

**Canonical implementation:** `examples/video_temporal_prototype.py` (commit `99867ae`)

Owns:
- Working memory + train-only retrieval + NumPy traffic tool (interlocked)
- Anti-contamination (`data/video_synth/fase1/SPLIT.json` 40 train / 10 eval; `CONTAMINATION_AUDIT.jsonl`)
- Dataset: `data/video_synth/fase1/` (1 street, 3 lights, 50×16 frames)
- Ablations: `python examples/video_temporal_prototype.py --ablate` → `data/video_synth/fase1/ABLATION_TABLE.md` (GPU; queued via `data/RUN_VIDEO_F1_WHEN_FREE.sh` / screen `qlora-video-f1`)

Locks: `docs/LOCK-THREE-LAYERS.md`, `docs/LOCK-ANTI-CONTAMINATION.md`.  
Quantum `data/lora_adapter/` = RO. No second street set. No GPU steal.
