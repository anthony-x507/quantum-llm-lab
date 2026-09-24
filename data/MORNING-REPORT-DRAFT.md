# QLab morning draft (ET) — 2026-09-24 noche

## Avance
- PASO1–5 cerrados: anti-fuga, smoke, full, diversity, rebalance rare-cues-first.
- Full rebalance train DONE 00:58 EXIT0: r32/α32/3ep 840 iters loss~1.93→0.025 peak~9.2GB → `data/lora_adapter/`.
- Eval rebalance DONE 01:30 EXIT0 PASS:
  - BASE parse/compile/Jev 0/0/0
  - FT 1.0/1.0/1.0 · domain 1.0 · label **0.9** · energy 1.0 · gate_combos **7**
  - ΔJev **+100%**
- Adapter **FROZEN** 01:32 ET (`data/NIGHT_ADAPTER_FREEZE.json` + `ADAPTER_FROZEN.lock`). No overwrite without archive.

## Dataset
- 280 rows · leak=0 · 7 fall templates (irregular 35 / wind 19 / ramp 17 / soft_ry 10 / drag 9 / soft_zry 9 / classic 3) · 11 gate-name combos in train.

## HOLD
- Desk F7 artifact quota
- QEC Fase 4 MLX hooks
- Cursor Cloud Agents (credit lock)

## Claims
LLM→JSON gates→PennyLane + Jev toy. **No** quantum advantage. QEC = pedagogical analogy.

## Next (día)
1. Morning report audio (08:19) — ya listo el draft.
2. Optional: larger n-test (30) daytime only; keep frozen adapter as baseline.
3. Optional: SERC paper skim / Agent-Lab notes — no Fase4.

## Night tip-of-spear (04:37 ET update)
- Ent-more train in flight on 380-row set → `lora_adapter_ent` (target 1140 iters).
- Parallel enrich landed: 11 bell + 11 sep templates; +80 scenes; `lora_dataset_ent_v2.jsonl` = 460 rows ready for next train after archive+eval.
- Claims unchanged: LLM→JSON→PennyLane+Jev toy; no quantum advantage; QEC Fase4 HOLD.

