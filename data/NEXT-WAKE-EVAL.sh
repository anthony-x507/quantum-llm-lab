#!/bin/bash
# Start rebalance eval only if train idle and no other eval/train lock.
set -euo pipefail
cd /Users/anthony/Documents/quantum-llm-lab
if pgrep -f 'examples/train_lora.py' >/dev/null; then
  echo "TRAIN still running — skip eval"
  exit 0
fi
if pgrep -f 'examples/eval_lora.py' >/dev/null; then
  echo "EVAL already running — skip"
  exit 0
fi
if [[ ! -f data/lora_adapter/adapters.safetensors ]]; then
  echo "No adapter — skip"
  exit 1
fi
# clear stale train lock if process gone
rm -f data/TRAIN_LOCK.txt
screen -wipe >/dev/null 2>&1 || true
screen -dmS qlab-eval-rebal bash -lc '
  cd /Users/anthony/Documents/quantum-llm-lab
  echo "pid=$$ screen=qlab-eval-rebal" > data/EVAL_LOCK.txt
  caffeinate -dims python examples/eval_lora.py \
    --model mlx-community/Qwen3-VL-8B-Thinking-4bit \
    --adapter data/lora_adapter \
    --n-test 10 \
    --out data/eval_compare_rebalance.json \
    2>&1 | tee -a data/eval_lora_rebalance.log
  echo EXIT:$? | tee -a data/eval_lora_rebalance.log
  echo DONE_AT:$(date) | tee -a data/eval_lora_rebalance.log
  rm -f data/EVAL_LOCK.txt
'
echo "Started screen qlab-eval-rebal"
screen -ls
