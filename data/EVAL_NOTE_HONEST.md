# Eval honesty note (2026-09-23 ~22:32 ET)

First `eval_compare.json` (pre-harden) looked like PASS (+50 Jev) but:

- **BASE:** 10/10 `source=fallback` (Thinking prose, no JSON) → metrics used **gold targets** → parse/compile 1.0 are inflated.
- **FINE-TUNE:** 9/10 real `source=vlm` JSON + 1 truncated Thinking; Jev APROBAR 9/10.

Real tip-of-spear signal: LoRA teaches **JSON emission** under the short prompt; base burns `max_tokens` on Thinking.

Hardened eval (commit aeab47b): train-aligned prompt, `max_tokens=512`, strip Thinking, **no gold inflate**. Re-eval in screen `qlab-eval2`.
