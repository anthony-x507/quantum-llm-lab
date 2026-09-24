# Collision predictive — CPU eval

ts: 2026-09-24 13:43:03 ET
audit: `data/eval_audit/collision_20260924_134302.jsonl`
contam_self_test.passed: True

## % collision correct (post-hoc GT)

| predictor | k=1 | k=3 | k=5 | overall |
|-----------|-----|-----|-----|---------|
| collision_physics | 100.0 | 100.0 | 100.0 | 100.0 |
| inverse_cv | 100.0 | 99.79 | 99.68 | 99.82 |
| collision_choose_safest | 100.0 | 100.0 | 100.0 | 100.0 |

**Ablation (collision − inverse_cv):** 0.18 pp

Positive → elastic collision layer improves consequence/safety prediction vs inverse-style CV (no mass/collision). Scored on action-conditional GT.

