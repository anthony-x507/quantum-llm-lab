# Full LoRA train summary (3 epochs, r32)

- Finished: 2026-09-23 22:17:32 EDT
- EXIT: 0
- Model: mlx-community/Qwen3-VL-8B-Thinking-4bit
- Adapter: `data/lora_adapter/` (~333MB final `adapters.safetensors`)
- Params: epochs=3 rank=32 alpha=32 lr=2e-4 batch=1 skip-eval
- Dataset: 280 rows (`data/lora_dataset.jsonl`), PASO1 anti-leak
- Iters: 840
- Loss: Iter10 ≈ 1.761 → Iter840 ≈ 0.009
- Peak mem: ~8.92 GB
- Throughput: ~0.55 it/s, ~200 tok/s
- Smoke adapter preserved: `data/lora_adapter_smoke/` (r16, 1ep)
- Eval: started 22:30 ET in screen `qlab-eval` → `data/lora_adapter/eval_compare.json`

## Eval caveat
First eval (`data/lora_adapter/eval_compare.json`) used old code: BASE fell back to gold on Thinking truncation → inflated parse/compile. FT emitted real JSON 9/10. Clean re-eval with hardened metrics → `data/eval_compare_clean.json` (in progress 22:32 ET).
