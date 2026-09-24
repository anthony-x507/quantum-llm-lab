# Amplitude embedding — results (Piece 1)

**When:** 2026-09-24 ~04:30 ET · **Claim:** no quantum advantage  
**Prototype:** `examples/amplitude_embed_prototype.py`  
**Mechanism:** PennyLane statevector → Re/Im (dim 8 for 2q) → SideMLP label probe; same features → seeded Linear → **embed_dim=4096** soft-prompt / `residual_first_token`. Not text/JSON.

## CPU eval (ENT_SET n=12, GPU held by `qlora-ent`)

| path | label_acc | energy_proxy_acc | notes |
|------|-----------|------------------|-------|
| amp-embed side-MLP (lib-trained) | **0.833** (10/12) | **1.000** | concurrence / S(ρ_A) proxy |
| library train acc (14 templates) | 1.000 | — | sanity, not test |
| base VLM (cached rebalance N=10, ent n=1) | **0.000** | 0.000 | no parseable JSON |
| LoRA text path RO `data/lora_adapter/` (cached rebalance) | **1.000** (ent n=1) / overall label 0.9 | 1.000 | **beats amp-embed** on generation usability |

**Honest conclusion:** Amplitude features *do* carry entangled/separable signal (0.83 label on held-out scenes). Soft-prompt residual into the frozen 8B was **not** MLX-evaluated yet (`TRAIN_LOCK` / `qlora-ent` mid-train). Even so, prior LoRA text path remains the stronger *generation* baseline — amp-embed does **not** claim to beat LoRA.

## MLX residual inject

Deferred until `data/TRAIN_LOCK.txt` clears. Command:

```bash
python examples/amplitude_embed_prototype.py --mlx-eval --adapter-ro data/lora_adapter
```

## Self-test

`python examples/amplitude_embed_prototype.py --self-test` → **PASS** (Bell concurrence≈1, product≈0, side-MLP 1.0, mlx inject helpers OK).
