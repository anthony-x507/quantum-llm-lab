# ENT_SET — código vivo Pillar 2 (entanglement)

**N:** 12 entanglement scenes · seed **20260924**
**Manifest:** `data/bench_live/ent_items.json`
**Scenes:** scene_0222, scene_0157, scene_0291, scene_0359, scene_0239, scene_0293, scene_0317, scene_0336, scene_0155, scene_0283, scene_0099, scene_0142

## Scoring (base vs adapter, same prompts)
- Load scene frame + anti-leak domain prompt (PASO1).
- Strip Thinking; `max_tokens≥512`.
- Parse JSON proposal → run PennyLane via `ejecutar_circuito`.
- Metrics (counts + %):
  - `label_correct` vs gold target label/gates when circuit **actually runs**
  - `energy_ok` via Jev energy rules on executed proposal
  - `parse_ok`, `compile_ok` / circuit_ran
  - domain_acc for entanglement
- Report execution errors honestly (parse fail, pennylane error).

## Note
Reinforces entanglement with gate variety from enrich dataset (380 scenes, 183 ent). Adapter under test is **baseline** `data/lora_adapter/` (or frozen archive) — READ-ONLY. Ent-more adapter `data/lora_adapter_ent/` is separate / post-train.
