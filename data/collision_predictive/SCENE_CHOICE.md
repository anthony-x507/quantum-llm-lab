# Scene choice (collision predictive)

Top-down **merge lane** with ego + vehicles/pedestrians (masses + radii).
Elastic disk collisions. Discrete hypo actions on ego.

Hardneg mix (choose_safest-n): unsafe-looking-but-safe, safe-looking-but-unsafe,
near-miss choice pressure — meta.hardneg_kind only; GT still post-hoc sidecar.

Deliberately **not** street-F1 (no multi-light intersection render),
**not** inverse corridor balls/boxes/signal, **not** quantum.
