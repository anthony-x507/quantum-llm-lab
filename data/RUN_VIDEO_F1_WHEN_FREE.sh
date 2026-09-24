#!/bin/bash
# TRAIN FIRST then measure. Own-delta only. Never touch data/lora_adapter/ (quantum RO).
# Anti-contam: TRAIN split LoRA only; ablations on eval; audit JSONL.
set -euo pipefail
cd /Users/anthony/Documents/quantum-llm-lab
LOG=data/train_video_f1.log
OUT=data/lora_adapter_video_f1
MODEL=mlx-community/Qwen3-VL-8B-Thinking-4bit
echo "VIDEO_F1_WAIT start=$(date) pid=$$" | tee "$LOG"

busy() {
  pgrep -f 'mlx_vlm.lora|examples/train_lora.py|examples/train_lora_classical.py' >/dev/null \
    || pgrep -f 'examples/eval_classical.py|examples/eval_lora.py|bench_codigo_vivo' >/dev/null \
    || pgrep -f 'video_temporal_prototype.py --train-f1|video_temporal_prototype.py --vlm|video_temporal_prototype.py --ablate|video_temporal_prototype.py --eval-compare' >/dev/null
}

for i in $(seq 1 480); do
  if busy || [[ -f data/TRAIN_LOCK.txt ]]; then
    echo "[$i] GPU/lock busy $(date +%H:%M:%S) lock=$(cat data/TRAIN_LOCK.txt 2>/dev/null | head -c 80)" | tee -a "$LOG"
    sleep 30
    continue
  fi
  echo "GPU_FREE at $(date) loop=$i — TRAIN F1 FIRST" | tee -a "$LOG"
  break
done

if busy || [[ -f data/TRAIN_LOCK.txt ]]; then
  echo "TIMEOUT still busy — exit without train" | tee -a "$LOG"
  exit 0
fi

# Ensure split + train-only dataset
.venv/bin/python examples/video_temporal_prototype.py --make-split 2>&1 | tee -a "$LOG"
.venv/bin/python examples/video_temporal_prototype.py --prepare-lora-dataset --max-frames 8 2>&1 | tee -a "$LOG"

echo "owner=video-f1 started=$(date -u +%Y-%m-%dT%H:%M:%SZ) out=$OUT rank=16 alpha=32 epochs=2" > data/TRAIN_LOCK.txt
set +e
caffeinate -dims .venv/bin/python examples/video_temporal_prototype.py --train-f1 --force-train \
  --rank 16 --alpha 32 --lr 2e-4 --epochs 2 --max-frames 8 \
  2>&1 | tee -a "$LOG"
TRC=${PIPESTATUS[0]}
echo "TRAIN_EXIT:$TRC $(date)" | tee -a "$LOG"
# release lock if we own it
if grep -q video-f1 data/TRAIN_LOCK.txt 2>/dev/null; then rm -f data/TRAIN_LOCK.txt; fi
set -e

if [[ ! -f $OUT/adapters.safetensors && ! -f $OUT/adapters.safetensors ]]; then
  # mlx may write file at output-path directly
  ls -la "$OUT" | tee -a "$LOG"
fi

if [[ $TRC -ne 0 ]]; then
  echo "TRAIN FAILED — skip measure (continuous: diagnose next wake)" | tee -a "$LOG"
  exit $TRC
fi

echo "MEASURE AFTER TRAIN: eval-compare (layers all) then ablations" | tee -a "$LOG"
set +e
caffeinate -dims .venv/bin/python examples/video_temporal_prototype.py --eval-compare --force-vlm \
  --adapter-ro "$OUT" --max-frames 8 --seq eval \
  2>&1 | tee -a "$LOG"
echo "EVAL_COMPARE_EXIT:$? $(date)" | tee -a "$LOG"

caffeinate -dims .venv/bin/python examples/video_temporal_prototype.py --ablate --force-vlm \
  --adapter-ro "$OUT" --max-frames 8 --seq eval \
  2>&1 | tee -a "$LOG"
echo "ABLATE_EXIT:$? $(date)" | tee -a "$LOG"
set -e

echo "VIDEO_F1_DONE $(date)" | tee -a "$LOG"
ls -la data/video_synth/fase1/results_base_vs_lora.json data/video_synth/fase1/ABLATION_TABLE.json data/video_synth/fase1/CONTAMINATION_AUDIT.jsonl 2>&1 | tee -a "$LOG"
