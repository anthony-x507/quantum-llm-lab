# Smoke LoRA summary (1 epoch)

- Date: 2026-09-23 21:51 ET
- Adapter out: `data/lora_adapter_smoke/`
- Script: `examples/train_lora.py` (PASO1 anti-leak; commits e2881e1 + 9db3f3b)
- Dataset: `data/lora_dataset.jsonl` (280 rows)

## Metrics (from train_lora_smoke.log)
```
Ejecutando: /Users/anthony/Documents/quantum-llm-lab/.venv/bin/python -m mlx_vlm.lora --model-path mlx-community/Qwen3-VL-8B-Thinking-4bit --dataset /Users/anthony/Documents/quantum-llm-lab/data/lora_dataset_hf --lora-rank 16 --lora-alpha 16.0 --learning-rate 0.0002 --epochs 1 --batch-size 1 --train-on-completions --grad-checkpoint --gradient-accumulation-steps 4 --output-path data/lora_adapter_smoke/adapters.safetensors
#trainable params: 43.646976 M || all params: 8767.123696 M || trainable%: 0.498%
[95mStarting training..., iterations: 280[0m
Iter 10: Train loss [92m2.04771118[0m, Learning Rate 2.000e-04, It/sec 0.634, Tokens/sec 229.582, Trained Tokens 3619, Peak mem 8.089 GB
Iter 20: Train loss [92m0.90406618[0m, Learning Rate 2.000e-04, It/sec 0.579, Tokens/sec 209.890, Trained Tokens 7242, Peak mem 8.089 GB
Iter 30: Train loss [92m0.56476688[0m, Learning Rate 2.000e-04, It/sec 0.563, Tokens/sec 202.276, Trained Tokens 10834, Peak mem 8.089 GB
Iter 40: Train loss [92m0.24761291[0m, Learning Rate 2.000e-04, It/sec 0.567, Tokens/sec 202.837, Trained Tokens 14411, Peak mem 8.089 GB
Iter 50: Train loss [92m0.21919785[0m, Learning Rate 2.000e-04, It/sec 0.558, Tokens/sec 204.120, Trained Tokens 18066, Peak mem 8.089 GB
Iter 60: Train loss [92m0.13527797[0m, Learning Rate 2.000e-04, It/sec 0.558, Tokens/sec 204.241, Trained Tokens 21728, Peak mem 8.225 GB
Iter 70: Train loss [92m0.07631336[0m, Learning Rate 2.000e-04, It/sec 0.570, Tokens/sec 206.389, Trained Tokens 25351, Peak mem 8.225 GB
Iter 80: Train loss [92m0.03214325[0m, Learning Rate 2.000e-04, It/sec 0.570, Tokens/sec 207.559, Trained Tokens 28994, Peak mem 8.225 GB
Iter 90: Train loss [92m0.06583201[0m, Learning Rate 2.000e-04, It/sec 0.578, Tokens/sec 202.488, Trained Tokens 32498, Peak mem 8.225 GB
Iter 100: Train loss [92m0.07747708[0m, Learning Rate 2.000e-04, It/sec 0.562, Tokens/sec 203.657, Trained Tokens 36124, Peak mem 8.225 GB
[94mIter 100: Saved adapter weights to data/lora_adapter_smoke/adapters.safetensors and data/lora_adapter_smoke/0000100_adapters.safetensors.[0m
Iter 110: Train loss [92m0.01702476[0m, Learning Rate 2.000e-04, It/sec 0.546, Tokens/sec 202.852, Trained Tokens 39840, Peak mem 8.225 GB
Iter 120: Train loss [92m0.02716165[0m, Learning Rate 2.000e-04, It/sec 0.554, Tokens/sec 199.050, Trained Tokens 43434, Peak mem 8.225 GB
Iter 130: Train loss [92m0.01854573[0m, Learning Rate 2.000e-04, It/sec 0.540, Tokens/sec 198.994, Trained Tokens 47118, Peak mem 8.225 GB
Iter 140: Train loss [92m0.05505758[0m, Learning Rate 2.000e-04, It/sec 0.554, Tokens/sec 199.880, Trained Tokens 50728, Peak mem 8.225 GB
Iter 150: Train loss [92m0.05592104[0m, Learning Rate 2.000e-04, It/sec 0.545, Tokens/sec 198.948, Trained Tokens 54381, Peak mem 8.225 GB
Iter 160: Train loss [92m0.01424660[0m, Learning Rate 2.000e-04, It/sec 0.551, Tokens/sec 199.131, Trained Tokens 57995, Peak mem 8.225 GB
Iter 170: Train loss [92m0.01667431[0m, Learning Rate 2.000e-04, It/sec 0.554, Tokens/sec 200.252, Trained Tokens 61607, Peak mem 8.225 GB
Iter 180: Train loss [92m0.02459735[0m, Learning Rate 2.000e-04, It/sec 0.555, Tokens/sec 201.444, Trained Tokens 65238, Peak mem 8.225 GB
Iter 190: Train loss [92m0.07518293[0m, Learning Rate 2.000e-04, It/sec 0.557, Tokens/sec 199.579, Trained Tokens 68818, Peak mem 8.225 GB
Iter 200: Train loss [92m0.02127817[0m, Learning Rate 2.000e-04, It/sec 0.560, Tokens/sec 202.129, Trained Tokens 72430, Peak mem 8.225 GB
[94mIter 200: Saved adapter weights to data/lora_adapter_smoke/adapters.safetensors and data/lora_adapter_smoke/0000200_adapters.safetensors.[0m
Iter 210: Train loss [92m0.01820209[0m, Learning Rate 2.000e-04, It/sec 0.562, Tokens/sec 203.830, Trained Tokens 76060, Peak mem 8.225 GB
Iter 220: Train loss [92m0.02214642[0m, Learning Rate 2.000e-04, It/sec 0.566, Tokens/sec 204.448, Trained Tokens 79670, Peak mem 8.225 GB
Iter 230: Train loss [92m0.00401870[0m, Learning Rate 2.000e-04, It/sec 0.557, Tokens/sec 204.047, Trained Tokens 83335, Peak mem 8.225 GB
Iter 240: Train loss [92m0.01179321[0m, Learning Rate 2.000e-04, It/sec 0.559, Tokens/sec 204.977, Trained Tokens 87000, Peak mem 8.225 GB
Iter 250: Train loss [92m0.02508804[0m, Learning Rate 2.000e-04, It/sec 0.570, Tokens/sec 204.329, Trained Tokens 90582, Peak mem 8.225 GB
Iter 260: Train loss [92m0.01085688[0m, Learning Rate 2.000e-04, It/sec 0.568, Tokens/sec 206.238, Trained Tokens 94212, Peak mem 8.225 GB
Iter 270: Train loss [92m0.01073730[0m, Learning Rate 2.000e-04, It/sec 0.570, Tokens/sec 205.813, Trained Tokens 97823, Peak mem 8.225 GB
Iter 280: Train loss [92m0.01736794[0m, Learning Rate 2.000e-04, It/sec 0.565, Tokens/sec 207.260, Trained Tokens 101494, Peak mem 8.225 GB
```

## Adapter files
```
total 1023400
-rw-r--r--@ 1 anthony  staff   167M Sep 23 21:44 0000100_adapters.safetensors
-rw-r--r--@ 1 anthony  staff   167M Sep 23 21:47 0000200_adapters.safetensors
-rw-r--r--@ 1 anthony  staff    14K Sep 23 21:49 adapter_config.json
-rw-r--r--@ 1 anthony  staff   167M Sep 23 21:49 adapters.safetensors
-rw-r--r--@ 1 anthony  staff   223B Sep 23 21:49 train_meta.json
```

## Notes
- Loss fell ~2.05 → 0.017 (smoke 1ep).
- Leak check PASS on 280-line jsonl.
- Do NOT overwrite smoke adapter; full train uses `data/lora_adapter/`.
