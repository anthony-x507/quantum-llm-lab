#!/usr/bin/env bash
# Wait for classical smoke priority + GPU free, then train ent_v2 (460) via NEXT-WAKE.
# Own-delta only. NEVER writes data/lora_adapter/ (quantum RO).
# Screen cmdline must NOT embed examples/train_lora.py (false-busy deadlock).
set -euo pipefail
cd /Users/anthony/Documents/quantum-llm-lab
LOG=data/ent_v2_wait.log
echo "ENT_V2_WAIT start=$(date) pid=$$" | tee "$LOG"

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

classical_done() {
  [[ -f data/lora_adapter_classical/adapters.safetensors ]] \
    || grep -qE 'CLASSICAL_SMOKE_DONE|EXIT:0' data/train_lora_classical_smoke.log 2>/dev/null \
    || grep -qE 'CLASSICAL_SMOKE_DONE|EXIT:0' data/classical_smoke.log 2>/dev/null
}

# screen -ls often exits 1 even when sessions exist — never use it under pipefail directly.
classical_screen_up() {
  local out
  out=$(screen -ls 2>/dev/null || true)
  [[ "$out" == *qlora-classical* ]]
}

# Prefer classical smoke FIRST
for k in $(seq 1 480); do
  if classical_done; then
    echo "classical cleared/done $(date) loop=$k" | tee -a "$LOG"
    break
  fi
  if classical_screen_up; then
    echo "[v2-wait classical $k] qlora-classical present $(date +%H:%M:%S)" | tee -a "$LOG"
    sleep 30
    continue
  fi
  if [[ -f data/TRAIN_LOCK.txt ]] && grep -q classical data/TRAIN_LOCK.txt 2>/dev/null; then
    echo "[v2-wait classical $k] lock=$(head -c 100 data/TRAIN_LOCK.txt) $(date +%H:%M:%S)" | tee -a "$LOG"
    sleep 30
    continue
  fi
  # classical screen absent and no classical lock — short grace then proceed only if still absent
  sleep 20
  if classical_done; then
    echo "classical cleared after grace $(date)" | tee -a "$LOG"
    break
  fi
  if classical_screen_up || { [[ -f data/TRAIN_LOCK.txt ]] && grep -q classical data/TRAIN_LOCK.txt 2>/dev/null; }; then
    echo "[v2-wait classical $k] classical returned during grace $(date +%H:%M:%S)" | tee -a "$LOG"
    continue
  fi
  echo "no classical screen/lock after grace — proceed $(date) loop=$k" | tee -a "$LOG"
  break
done

# Wait until no real python train and no TRAIN_LOCK
for i in $(seq 1 480); do
  if busy; then
    echo "[v2-wait gpu $i] real train busy $(date +%H:%M:%S)" | tee -a "$LOG"
    sleep 30
    continue
  fi
  if [[ -f data/TRAIN_LOCK.txt ]]; then
    echo "[v2-wait gpu $i] TRAIN_LOCK $(head -c 100 data/TRAIN_LOCK.txt) $(date +%H:%M:%S)" | tee -a "$LOG"
    sleep 30
    continue
  fi
  echo "GPU_FREE for ent_v2 at $(date) loop=$i" | tee -a "$LOG"
  break
done

if busy || [[ -f data/TRAIN_LOCK.txt ]]; then
  echo "TIMEOUT still busy — exit without ent_v2 train $(date)" | tee -a "$LOG"
  exit 0
fi

bash data/NEXT-WAKE-TRAIN-ENT-V2.sh 2>&1 | tee -a "$LOG"
echo "ENT_V2_WAIT_DONE $(date)" | tee -a "$LOG"
