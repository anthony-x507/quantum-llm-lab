# Estado de avance

Ver **[`docs/STATUS.md`](docs/STATUS.md)** (Agent Lab / quantum-llm-lab).  
Plan SSOT: [`docs/PLAN-MAESTRO-PARTE-1.md`](docs/PLAN-MAESTRO-PARTE-1.md).

## 2026-09-24 — fold tip-own-delta-scoreboard → codigo-vivo-tip
Rebase `2382c90` onto `0a1ef4d` → `66db30a` FF. CPU unified **1.0**; R1–R4 18/18·22/22·35/35·40/40; R3/R4 verifier 28/28·32/32; `wired_to_vlm=true`. Own-delta honesty retained (Py−0.062 Ent+1.0 Vis−0.200; dual-lane protects). Freezes retained + post_polish. See SCOREBOARD + OWN-DELTA-SCOREBOARD.

## 2026-09-24 — fold tip-ent-sep-fix → codigo-vivo-tip
Rebase `47975a7` onto `459f6da` → `08463a2` FF. CPU unified 1.0; MLX ent2-with-sep 1.0 (`scene_0222` held). LIVE honest pool → `mixed_items_largern.json`. Freezes retained. See docs/FRONTIER-CODIGO-VIVO-TIP-ENT-SEP-FIX.md + SCOREBOARD.

## 2026-09-24 — tip-own-delta-scoreboard

Branch `frontier/tip-own-delta-scoreboard` from tip `459f6da` (rebase onto tip with ent-sep → `66db30a`).  
Own-delta tip: Py Δ **−0.062** (hurt; tip avoids), Ent **+1.0** (ent2 helps), Vis **−0.200** (hurt; tip uses BASE).  
Tip dual-lane CPU+MLX sample unified **1.0**. Anti-contam **CLEAN**. Adapters RO unchanged.  
See `docs/FRONTIER-CODIGO-VIVO-TIP-OWN-DELTA-SCOREBOARD.md`.
