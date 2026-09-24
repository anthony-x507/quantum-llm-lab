# Frontier — vision MLX anti-think (JSON parse)

**Branch:** `frontier/vision-mlx-anti-think` (stacked on `frontier/vision-mlx-api-fix` @ `62843ad`)  
**Host:** Mac-111 · **Model:** `mlx-community/Qwen3-VL-8B-Thinking-4bit`  
**Evidence:** `data/frontier_vision_mlx_anti_think_mac111.json`  
**Written:** 2026-09-24 ~10:57 ET

## Problem

API call shape was already fixed (`generate(model, processor, prompt, image=…)`).  
With `max_tokens=768`, Thinking-4bit burned the budget on English prose (“Got it, let’s analyze…”) and never emitted JSON → **parse 0/3**.

## Fix (anti-think, lab pattern)

In `vision/grounding.py` (keep `generate(…, image=sample)` shape; demo/CPU unchanged):

1. **`max_tokens=1536`** phase-1 headroom (jev uses ≥1024 for Thinking).
2. **Strip** `<think>` / `<thinking>` + brace-balanced JSON extract (jev + `train_lora._strip_thinking`).
3. **Force JSON cue** (jev-style): “ÚNICAMENTE… empiece con `{`… Sin cadena de pensamiento en inglés.”
4. **Two-phase:** if phase-1 parse fails → JSON-only retry (`max_tokens=512`, no-think prompt).

## Result (n=3)

| | parse_ok | parse_rate | tokens budget |
|--|--|--|--|
| Before (`62843ad`) | 0/3 | 0.0 | 768 |
| After (anti-think) | **3/3** | **1.0** | 1536 (+512 retry if needed) |

All 3 hits were **phase=`think_then_json`** (retry unused). CPU `--demo` PASS. Minimal API smoke PASS.

## Ceiling note

On this host/model, **no honest ceiling** hit for structured grounding JSON once budget ≥1536 + JSON cue: 3/3 usable.  
If a future Thinking checkpoint regresses to prose-only within 1536, phase-2 JSON-only is the recovery path; document any residual fail rate there rather than raising tokens blindly.
