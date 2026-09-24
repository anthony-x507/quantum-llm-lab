#!/bin/bash
# LOCK: after smoke, eval BASE vs data/lora_adapter_classical only (own-delta). No Gemini/GPT.

# Wait until GPU free, then 1ep classical smoke → data/lora_adapter_classical/
# NEVER writes to data/lora_adapter/ (quantum READ-ONLY).
set -euo pipefail
cd /Users/anthony/Documents/quantum-llm-lab
LOG=data/train_lora_classical_smoke.log
OUT=data/lora_adapter_classical
MODEL=mlx-community/Qwen3-VL-8B-Thinking-4bit
echo "CLASSICAL_SMOKE_WAIT start=$(date) pid=$$" | tee "$LOG"

busy() {
  # Real GPU owners: Python interpreter running train/eval.
  # macOS `comm` is a truncated path — match on full command= instead.
  # Exclude bash/zsh/SCREEN waiters and agent shells.
  ps ax -o pid=,command= 2>/dev/null | awk '
    BEGIN { found=0 }
    {
      line=$0
      if (line ~ /\/bin\/(ba)?sh / || line ~ /\/bin\/zsh / || line ~ /SCREEN / || line ~ /^[[:space:]]*[0-9]+[[:space:]]+login /) next
      if (line !~ /\/MacOS\/Python / && line !~ /\/python[0-9.]* / && line !~ /\/python /) next
      if (line ~ /examples\/train_lora\.py/) found=1
      else if (line ~ /mlx_vlm\.lora/) found=1
      else if (line ~ /train_lora_classical/) found=1
      else if (line ~ /eval_classical\.py/) found=1
      else if (line ~ /eval_lora\.py/) found=1
      else if (line ~ /bench_codigo/) found=1
      else if (line ~ /amplitude_embed/) found=1
      else if (line ~ /video_temporal_prototype\.py/ && line ~ /--(train-f1|vlm|ablate|eval-compare)/) found=1
    }
    END { exit found ? 0 : 1 }
  '
}

for i in $(seq 1 360); do
  if busy; then
    echo "[$i] GPU busy $(date)" | tee -a "$LOG"
    sleep 30
    continue
  fi
  if [[ -f data/TRAIN_LOCK.txt ]]; then
    echo "[$i] TRAIN_LOCK present $(date) :: $(cat data/TRAIN_LOCK.txt)" | tee -a "$LOG"
    sleep 30
    continue
  fi
  echo "GPU_FREE at $(date) loop=$i — starting classical smoke 1ep" | tee -a "$LOG"
  break
done

if busy; then
  echo "TIMEOUT still busy — exit without train" | tee -a "$LOG"
  exit 0
fi

echo "owner=classical-smoke started=$(date -u +%Y-%m-%dT%H:%M:%SZ) out=$OUT rank=16 alpha=16 epochs=1" > data/TRAIN_LOCK.txt
set +e
caffeinate -dims python examples/train_lora_classical.py \
  --model "$MODEL" \
  --out "$OUT" \
  --rank 16 --alpha 16 --lr 2e-4 --epochs 1 \
  2>&1 | tee -a "$LOG"
EC=${PIPESTATUS[0]}
set -e
echo EXIT:$EC | tee -a "$LOG"
echo DONE_AT:$(date) | tee -a "$LOG"
rm -f data/TRAIN_LOCK.txt

if [[ $EC -eq 0 ]] && ! busy; then
  caffeinate -dims python examples/eval_classical.py \
    --adapter "$OUT" \
    --quantum-adapter data/lora_adapter \
    --n-test 16 \
    --out data/BENCHMARK_CLASSICAL.json \
    2>&1 | tee -a data/eval_classical_smoke.log || true
fi

# CONTINUOUS SELF-IMPROVE (Anthony 04:38): after smoke+own-delta eval, if match rises vs base → extend epochs or harden hard cases; if falls → diagnose subdomain fails and regenerate/fix — never exit "done forever".
