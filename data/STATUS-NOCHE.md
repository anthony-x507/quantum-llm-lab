# STATUS-NOCHE — tip-of-spear entanglement

**Updated:** 2026-09-24 04:39:22 EDT

## Live train (do not kill)
- Screen: `qlora-ent` + waiter `qlab-after-ent`
- Adapter out: `data/lora_adapter_ent/`
- Dataset in use: `data/lora_dataset_hf` (380 rows, pre-v2)
- Progress: **Iter 730 / 1140** · loss≈92 · It/sec≈0.495 · ETA≈13.8 min
- Lock: `data/TRAIN_LOCK.txt` owner=tip-of-spear-ent-more
- Classical smoke: `qlora-classical` politely waiting GPU (OK)

## Parallel enrich (this wake, CPU-only)
- Added **4 bell + 4 sep** templates (now bell=11, sep=11 distinct gate fingerprints)
- Generated **80** new ent scenes → `scene_0380`…`scene_0459`
- Staged next JSONL: `data/lora_dataset_ent_v2.jsonl` (**460** rows; ent 263 / fall 102 / super 95)
- Did **not** touch live `lora_dataset_hf` or kill train

## After current train (waiter already queued)
1. Pillars bench (frozen baseline adapter)
2. Ent eval → `ENT_ITER_NOTE.md`
3. **Next idle wake:** run `data/NEXT-WAKE-TRAIN-ENT-V2.sh` (archives adapter, trains on v2)

## HOLD
- QEC Fase4
- Desk F7
- No quantum-advantage claims (LLM→JSON→PennyLane+Jev toy only)
