# After ent_v6 train+eval: next train = ent_v8 hardneg

- Dataset ready: `data/lora_dataset_ent_v8.jsonl` (**1028** rows; +56 ent 920–975 +24 fall 976–999 +24 super 1000–1023 +4 forced 1024–1027; **34 bell + 35 sep** pools / 34+34 in jsonl)
- Prior staged kept: v2=520 / v3=520 / v4=608 / v5=712 / v6=920 / v7=920. Do not clobber live hf until v6 train done.
- Prefer out dir `data/lora_adapter_ent3/` (or archive ent2 then reuse ent2)
- PASO1 leak=0 on v8; own-delta eval vs ent_v6/v2 + archives + frozen rebalance
- New hardneg: bell_ryxhcxz/hcxxy/yxhcxry/zhycx + sep_hyz/ryxz/xhy/zhry
- Claims: LLM→JSON→PennyLane+Jev toy only; no quantum-advantage; QEC Fase4 HOLD
- Written: 2026-09-24 07:38:36 EDT
