# THREE LAYERS prototype — status

**Owner:** video F1 (`examples/video_temporal_prototype.py`, commit `99867ae`)  
**Dataset:** `data/video_synth/fase1/` · split `SPLIT.json` (40 train / 10 eval)  
**Adapter target:** `data/lora_adapter_video_f1/` (quantum `data/lora_adapter/` RO)  
**No quantum-advantage claims.**

## Layers (interlocked)

| Layer | Role | Anti-contam rule |
|-------|------|------------------|
| Working memory | perceptions / own preds across frames | never GT/labels |
| Retrieval | train-only NN index | eval IDs refused; leak → INVALID |
| Tool use | NumPy traffic/physics compute | never dataset answer keys |

## Ablation

```bash
python examples/video_temporal_prototype.py --ablate
```

| ablation | memory | retrieval | tool |
|----------|--------|-----------|------|
| none | — | — | — |
| memory | ✓ | — | — |
| retrieval | — | ✓ | — |
| tool | — | — | ✓ |
| all | ✓ | ✓ | ✓ |

**Outputs (when GPU free):**
- `data/video_synth/fase1/ABLATION_TABLE.md` + `.json`
- Audit: `data/video_synth/fase1/CONTAMINATION_AUDIT.jsonl` (and/or `data/eval_audit/`)
- Own deltas vs `none` baseline (same 8B path)

**Status 2026-09-24 ~04:44 ET:** table **pending GPU** — screen `qlora-video-f1` waits behind `qlora-ent` / classical. CPU layers+split+GT-oracle already shipped; do **not** rebuild a second street set.

## Inverse-planning

Separate domain (other executor). Not part of this prototype.
