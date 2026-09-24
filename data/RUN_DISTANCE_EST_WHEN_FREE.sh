#!/bin/bash
# Distance-est LoRA — FLOOR-SCALE. Queue behind ALL existing GPU waiters.
# NEVER touch data/lora_adapter/ (quantum RO). Adapter → data/lora_adapter_distance/
# Do NOT start if screens qlora-ent / classical / video-f1 / etc. hold GPU.
set -euo pipefail
cd /Users/anthony/Documents/quantum-llm-lab
LOG=data/train_distance_est.log
OUT=data/lora_adapter_distance
MODEL=mlx-community/Qwen3-VL-8B-Thinking-4bit
echo "DISTANCE_EST_WAIT start=$(date) pid=$$ scale=FLOOR-SCALE" | tee "$LOG"

busy() {
  pgrep -f 'mlx_vlm.lora|examples/train_lora.py|examples/train_lora_classical.py' >/dev/null \
    || pgrep -f 'examples/eval_classical.py|examples/eval_lora.py|bench_codigo_vivo' >/dev/null \
    || pgrep -f 'video_temporal_prototype.py --train-f1|video_temporal_prototype.py --vlm|video_temporal_prototype.py --ablate' >/dev/null \
    || pgrep -f 'examples/distance_est/' >/dev/null \
    || [[ -f data/TRAIN_LOCK.txt ]]
}

# Long wait — behind ent + classical + video_f1 (+ enrich waiters)
for i in $(seq 1 720); do
  if busy; then
    echo "[$i] GPU/lock busy $(date +%H:%M:%S) lock=$(cat data/TRAIN_LOCK.txt 2>/dev/null | head -c 80)" | tee -a "$LOG"
    sleep 30
    continue
  fi
  echo "GPU_FREE at $(date) loop=$i — DISTANCE EST train (FLOOR-SCALE)" | tee -a "$LOG"
  break
done

if busy; then
  echo "TIMEOUT still busy — exit without train" | tee -a "$LOG"
  exit 0
fi

echo "owner=distance-est-floor-scale started=$(date -u +%Y-%m-%dT%H:%M:%SZ) out=$OUT" > data/TRAIN_LOCK.txt
echo "STAGED: LoRA train script not yet wired to VLM JSONL — CPU heuristic shipped. Releasing lock." | tee -a "$LOG"
rm -f data/TRAIN_LOCK.txt
echo "DONE staged $(date)" | tee -a "$LOG"
