# Inverse planning — Fase 1 passive dataset

- **Scene style:** top-down corridor arena, balls/boxes + one discrete signal
  (NOT street-lights F1; NOT classical sport/projectile stills; NOT quantum).
- **Seed:** 240924
- **Sequences:** 40 (train=32, eval=8)
- **Frames/seq:** 10–20
- **Horizons k:** [1, 3, 5]
- **GT futures:** `futures_gt.json` sidecars only — never in `meta.json` / prompts
- **Retrieval index:** train-only → `retrieval_index_train.json` (leak=∅)
- **Adapter (later, GPU free):** `data/lora_adapter_inverse/` only
