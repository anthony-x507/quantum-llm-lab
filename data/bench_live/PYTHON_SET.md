# PYTHON_SET — código vivo Pillar 1

**Purpose:** Small custom executable-Python bench (NOT full GSM8K/HumanEval).
**N:** 16 items · balanced across arithmetic / algebra_word / script
**Created:** 2026-09-24 04:22:23 
**Manifest:** `data/bench_live/python_items.json`

## Scoring
1. Prompt model (base `adapter=null` vs LoRA) to emit **Python only** (strip Thinking + markdown fences).
2. Run in sandbox subprocess: `python3 -I` (isolated), cwd temp, timeout 5s, no network assumed (no socket open by harness).
3. Compare **stdout** to `expected_stdout` (exact string after normalizing trailing newline).
4. Metric: **% solved** = correct_stdout / N. Report execution errors honestly (SyntaxError, Timeout, nonzero exit).

## Item inventory
| id | kind | expected stdout |
|----|------|-----------------|
| `py_arith_01` | arithmetic | `65` |
| `py_arith_02` | arithmetic | `125` |
| `py_arith_03` | arithmetic | `14` |
| `py_arith_04` | arithmetic | `1024` |
| `py_alg_01` | algebra_word | `64` |
| `py_alg_02` | algebra_word | `7` |
| `py_alg_03` | algebra_word | `18` |
| `py_alg_04` | algebra_word | `10` |
| `py_script_01` | script | `55` |
| `py_script_02` | script | `3` |
| `py_script_03` | script | `720` |
| `py_script_04` | script | `5` |
| `py_script_05` | script | `yes` |
| `py_script_06` | script | `edcba` |
| `py_script_07` | script | `6` |
| `py_script_08` | script | `6` |

## Anti-claims
No quantum-advantage language. This pillar measures **executable Python emission + correct stdout**, not quantum speedups.
