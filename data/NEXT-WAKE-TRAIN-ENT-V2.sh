#!/usr/bin/env bash
# After current ent train+eval finishes: archive adapter, train on v2 enriched set.
set -euo pipefail
cd "$(dirname "$0")/.."
if ps ax -o pid=,command= 2>/dev/null | awk '
  BEGIN { found=0 }
  {
    line=$0
    if (line ~ /\/bin\/(ba)?sh / || line ~ /\/bin\/zsh / || line ~ /SCREEN /) next
    if (line !~ /\/MacOS\/Python / && line !~ /\/python[0-9.]* / && line !~ /\/python /) next
    if (line ~ /examples\/train_lora\.py/ || line ~ /mlx_vlm\.lora/) found=1
  }
  END { exit found ? 0 : 1 }
'; then
  echo "GPU train still running — abort"; exit 1
fi
TS=$(date +%Y%m%d-%H%M%S)
if [[ -f data/lora_adapter_ent/adapters.safetensors ]]; then
  arch="data/lora_adapter_ent_archived_${TS}"
  mkdir -p "$arch"
  cp -R data/lora_adapter_ent/* "$arch/" || true
  echo "archived -> $arch"
fi
cp data/lora_dataset_ent_v2.jsonl data/lora_dataset.jsonl
rm -rf data/lora_dataset_hf
echo "owner=tip-of-spear-ent-v2 started=$(date -u +%Y-%m-%dT%H:%M:%SZ) out=data/lora_adapter_ent rows=460" > data/TRAIN_LOCK.txt
screen -dmS qlora-ent-v2 bash -lc '
  cd /Users/anthony/Documents/quantum-llm-lab
  echo "START_V2 $(date) pid=$$" | tee data/train_lora_ent_v2.log
  caffeinate -dims python examples/train_lora.py \
    --model mlx-community/Qwen3-VL-8B-Thinking-4bit \
    --out data/lora_adapter_ent \
    --dataset-jsonl data/lora_dataset_ent_v2.jsonl \
    --rank 32 --alpha 32 --lr 2e-4 --epochs 3 \
    --skip-eval \
    2>&1 | tee -a data/train_lora_ent_v2.log
  echo EXIT:$? | tee -a data/train_lora_ent_v2.log
  echo DONE_AT:$(date) | tee -a data/train_lora_ent_v2.log
  rm -f data/TRAIN_LOCK.txt
'
echo "started qlora-ent-v2"
