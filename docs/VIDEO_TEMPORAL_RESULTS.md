# VIDEO temporal understanding — Fase 1 results

**When:** 2026-09-24 ~04:35–04:45+ ET  
**Locks:** TRAIN FIRST → measure AFTER · own-delta only (no Gemini/GPT) · quantum `data/lora_adapter/` **RO**  
**Layout:** ONE street · THREE lights · ≥50 synth GT  
**Adapter:** `data/lora_adapter_video_f1/` (NEW)  
**Prototype:** `examples/video_temporal_prototype.py`

## Three layers (interlocked)

| layer | role | anti-contam |
|-------|------|-------------|
| **Working memory** | Buffer objects / preds / light state across frames; consult before answer | Perceptions + tool outs only — **never GT labels** |
| **Retrieval** | Train-only index; nearest by memory features; schema/style hint | **TRAIN split only**; eval id in index → INVALID |
| **Tool** | NumPy traffic/light kinematics + pairwise risk | Real compute from perceptions — **never answer keys** |

Flow: memory → retrieval → tool → memory → VLM final JSON.

## Anti-contamination

- Split: `data/video_synth/fase1/SPLIT.json` — **40 train / 10 eval**, overlap=∅
- LoRA JSONL: TRAIN ids only (`fase1_lora_dataset_hf/`)
- Eval GT used **post-hoc for scoring only** — never in prompt/memory/retrieval/tool
- Audit log: `data/video_synth/fase1/CONTAMINATION_AUDIT.jsonl` (every eval: layers, memory snapshot, retrieval hit, tool call, `prompt_touches_gt`)
- Dirty run → mark INVALID, discard numbers, rerun

## Dataset

| item | value |
|------|-------|
| sequences | 50 × 16 frames |
| train / eval | 40 / 10 |
| LoRA rows | 40 (train-only) |
| F2/F3 | CPU scaffolds under `data/video_synth/fase2|fase3/` — **no GPU train until F1 gate** |

## GT-oracle plumbing

Oracle aggregate tracking/coherent/light_state = 1.0 (scoring path OK).

## Train / measure status

Queued: `screen qlora-video-f1` → `data/RUN_VIDEO_F1_WHEN_FREE.sh`  
Waits until `TRAIN_LOCK` / foreign mlx clear → **train** → `--eval-compare` (layers all) → `--ablate`.

### Base vs LoRA (layers all, eval split) — fill after train

| metric | base | LoRA | Δ |
|--------|------|------|---|
| % tracking correct | _pending_ | _pending_ | _pending_ |
| % resumen coherente | _pending_ | _pending_ | _pending_ |
| gate (≥80% both or clear jump) | _pending_ | | |

### Ablations table — fill after `--ablate`

See `data/video_synth/fase1/ABLATION_TABLE.md` (clean rows only).

| ablation | track | coherent | Δtrack vs none | dirty |
|----------|-------|----------|----------------|-------|
| none / memory / retrieval / tool / all | _pending_ | | | |

## Recommendation (living)

- Continuous self-improve: if Δ rises → stack F2 reinforcement (generators ready); if falls → diagnose `tracking_by_type` + audit log → fix set/prompt/train — **no idle on high score**, **no F2 LoRA until F1 gate**.
- Never report dirty / leaked numbers.

## Commands

```bash
python examples/video_temporal_prototype.py --generate-f1 --n-seq 50 --n-frames 16
python examples/video_temporal_prototype.py --make-split --prepare-lora-dataset
# when GPU free:
bash data/RUN_VIDEO_F1_WHEN_FREE.sh
# or:
python examples/video_temporal_prototype.py --train-f1 --rank 16 --epochs 2
python examples/video_temporal_prototype.py --eval-compare --adapter-ro data/lora_adapter_video_f1 --seq eval --force-vlm
python examples/video_temporal_prototype.py --ablate --adapter-ro data/lora_adapter_video_f1 --seq eval --force-vlm
```
