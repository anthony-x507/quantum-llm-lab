# Collision predictive — CPU eval

ts: 2026-09-24 13:08:58 ET
audit: `data/eval_audit/collision_20260924_130857.jsonl`
contam_self_test.passed: True

## % collision correct (post-hoc GT)

| predictor | k=1 | k=3 | k=5 | overall |
|-----------|-----|-----|-----|---------|
| collision_physics | 100.0 | 100.0 | 100.0 | 100.0 |
| inverse_cv | 94.05 | 85.95 | 75.68 | 85.23 |
| collision_choose_safest | 100.0 | 100.0 | 100.0 | 100.0 |

**Ablation (collision − inverse_cv):** 14.77 pp

Positive → elastic collision layer improves consequence/safety prediction vs inverse-style CV (no mass/collision). Scored on action-conditional GT.

