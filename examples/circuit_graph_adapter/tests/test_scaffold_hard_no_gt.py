"""Hard fixtures: scaffold hints stay GT-free; families route to ent."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "examples"))

import circuit_graph_moe_scaffold as sc  # noqa: E402
import moe_dual_lane_router as moe  # noqa: E402

_FORBIDDEN = re.compile(
    r"\b(label|gold|gt|ground.?truth|collapsed_to|y_true|target_label)\b",
    re.I,
)


def test_hard_fixtures_count_and_families():
    assert len(sc.HARD_FIXTURES) >= 12
    ids = {fx["id"] for fx in sc.HARD_FIXTURES}
    assert any(i.startswith("hard_teleport") for i in ids)
    assert any(i.startswith("hard_qft") for i in ids)
    assert any(i.startswith("hard_parity") for i in ids)
    assert any(i.startswith("hard_trap") for i in ids)
    assert any("cluster" in i or i.startswith("hard_w") for i in ids)


def test_hard_hints_have_no_gt_tokens():
    for fx in sc.HARD_FIXTURES:
        hint = sc.format_scaffold_hint(fx["prompt"], polish=True)
        assert sc.SCAFFOLD_BEGIN in hint
        assert _FORBIDDEN.search(hint) is None


def test_hard_fixtures_route_ent():
    for fx in sc.HARD_FIXTURES:
        assert moe.route(fx["prompt"], method="heuristic") == "ent", fx["id"]


def test_freeze_file_not_required_writable(tmp_path, monkeypatch):
    """maybe_freeze must no-op when freeze already exists."""
    assert sc.FREEZE_OUT.exists()
    fake = {
        "clear_win": True,
        "delta_scaffold_minus_off": {"parse_rate": 1, "structure_rate": 1, "solve_rate": 1},
        "n_ent_evaluated": 20,
        "polish_features": False,
        "claims": [],
        "anti_contamination": {},
    }
    assert sc.maybe_freeze(fake, allow_write=True) is None
