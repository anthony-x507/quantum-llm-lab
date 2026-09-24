# VISION_SET — código vivo Pillar 3

**N:** 13 image→answer items (math + circuit diagrams rendered as PNG)
**Manifest:** `data/bench_live/vision_items.json`
**Images:** `data/bench_live/vision_items/*.png`
**Created:** 2026-09-24 04:22:23 · **circ expand:** 2026-09-24 14:12:25 ET 

## Scoring
- Multimodal prompt with image; strip Thinking; max_tokens≥512.
- Math items: extract integer / exact expected string.
- Circuit items: parse JSON gates; require expected gate names present + n_qubits.
- Metric: **% correct**. Note: vision helps image→answer more than pure code generation.
- Circ expand (tip-circ-expand side): +3 grounded circuit scenes (Bell-only, GHZ-3q, X+RY+CNOT). Tip vis stays BASE.

## Inventory
| id | kind | expected |
|----|------|----------|
| `vis_math_01` | math | `45` |
| `vis_math_02` | math | `50` |
| `vis_math_03` | math | `20` |
| `vis_math_04` | math | `6` |
| `vis_math_05` | math | `20` |
| `vis_math_06` | math | `48` |
| `vis_circ_01` | circuit | `H,X,CNOT` |
| `vis_circ_02` | circuit | `RY,Z` |
| `vis_math_07` | math | `20` |
| `vis_math_08` | math | `45` |
| `vis_circ_03` | circuit | `H,CNOT` (2q Bell-only) |
| `vis_circ_04` | circuit | `H,CNOT` (3q GHZ) |
| `vis_circ_05` | circuit | `X,RY,CNOT` |

No quantum-advantage claims.
