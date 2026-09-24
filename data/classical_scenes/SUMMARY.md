# Classical visual physics dataset SUMMARY

- n_scenes: 220
- seed: 240924
- frame size: 240x180
- lane: classical_visual_physics (NOT quantum)
- gold_python verified: 220/220

## Domain totals
- sport_balls (baseball/soccer/golf): 84
- rockets_projectiles: 136

## Counts by subdomain
- angled_projectile: 27
- ballistic: 28
- baseball: 28
- drag_projectile: 27
- elastic_collision: 27
- golf: 28
- inelastic_collision: 27
- soccer: 28

## Ground-truth metrics
Each `meta.json` has `params`, `expected_metrics` (`range_m`, `max_height_m`, `impact_speed_m_s`), and `tolerance`.
Assistant target = executable Python (`gold_python`) that prints those metrics.

## Anti-leak
User prompts must NOT include gold numeric metrics; only qualitative visual cues.

## READ-ONLY note
`data/lora_adapter/` (quantum) is never a write target for this lane.
Classical adapters go to `data/lora_adapter_classical/`.
