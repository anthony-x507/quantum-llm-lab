#!/bin/bash
# Wait until GPU free, then 1ep classical smoke → data/lora_adapter_classical/
# NEVER writes to data/lora_adapter/ (quantum READ-ONLY).
set -euo pipefail
cd /Users/anthony/Documents/quantum-llm-lab
LOG=data/train_lora_classical_smoke.log
OUT=data/lora_adapter_classical
MODEL=mlx-community/Qwen3-VL-8B-Thinking-4bit
echo "CLASSICAL_SMOKE_WAIT start=$(date) pid=$$" | tee "$LOG"

busy() {
  pgrep -f 'mlx_vlm.lora|examples/train_lora.py|examples/train_lora_classical.py' >/dev/null \
    || pgrep -f 'examples/eval_classical.py|examples/eval_lora.py|bench_codigo_vivo|bench_codigo' >/dev/null \
    || pgrep -f 'examples/amplitude_embed' >/dev/null
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
