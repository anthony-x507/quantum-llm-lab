# Eval post nota_fix (2026-09-23 ~23:30 ET)

Adapter: `data/lora_adapter/` (retrain r32/α32/3ep after nota+Jev Regla2 patch; now archived as `lora_adapter_pre_diversity_*` before diversity retrain).

## Clean metrics (n=10, no gold inflate)

| | parse | compile | Jev APROBAR |
|--|------:|--------:|------------:|
| BASE | 0.0 | 0.0 | 0.0 |
| FT | 1.0 | 1.0 | 1.0 |
| Δ | +1.0 | +1.0 | **+100% PASS** (meta ≥+20) |

Report: `data/eval_compare_nota_fix.json`

Prior clean (pre-nota_fix): ΔJev +40% but 6/10 Regla2 false-positives on gold wording.
After nota wording + arbiter negation fix: 10/10 APROBAR.

## Next
PASO5+: 7 fall templates (ramp_yry/soft_zry/soft_ry/wind_dual_ry/drag_bounce/irregular_xry/classic_hcxry), label/domain/energy metrics in eval, diversity retrain overnight.
