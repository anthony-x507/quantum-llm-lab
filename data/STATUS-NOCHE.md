# STATUS-NOCHE — tip-of-spear entanglement

**Updated:** 2026-09-24 07:38:36 EDT

## Live now
- **qlora-ent-v6** training healthy → `data/lora_adapter_ent2/` (r32/α32/3ep, 2760 iters)
- Progress: Iter ~230/2760 · Train loss [92m0.05023417[0m · It/sec 0.517 · peak≈9.05 GB
- TRAIN_LOCK: tip-of-spear-ent-v6 (live hf → `data/lora_dataset_ent_v6.jsonl` 920)
- Waiter: qlab-classical-eval (yielding)

## Just finished (this wake)
- CPU enrich **ent_v8** staged: +4 bell +4 sep → pools **34 bell / 35 sep** (jsonl coverage 34/34)
- Scenes 0920–1027 (+108); `data/lora_dataset_ent_v8.jsonl` = **1028** (ent 591 / fall 222 / super 215); PASO1 leak=0
- Live hf + v6 jsonl untouched; quantum `data/lora_adapter/` RO @00:58:09

## Do not kill
- Screens: qlora-ent-v6, qlab-classical-eval
- Frozen quantum adapter RO: `data/lora_adapter/` (00:58:09)

## Staged next
1. ent_v6 train DONE → own-delta eval vs ent_v2 + archive + frozen
2. Then ent_v7 (920) or prefer **ent_v8 (1028)** for gate diversity
3. Classical own-delta eval when GPU free

## HOLD
- QEC Fase4 · Desk F7 · No quantum-advantage claims
