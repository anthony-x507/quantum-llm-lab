#!/usr/bin/env python3
"""Unified evidence logger for quantum-llm-lab (stdlib-first).

ALWAYS-record schema for eval/runs with optional visual evidence paths.
Does NOT touch GPU, TRAIN_LOCK, screens, or data/lora_adapter/.

Reuse alongside existing sinks:
  - data/experiment_log.jsonl / experiment_log_v2.jsonl
  - data/eval_audit/*.jsonl
  - data/eval_compare_*.json
  - data/hybrid_oracle/report.json
  - video_synth frames under data/video_synth/

CLI:
  python examples/evidence_run_logger.py demo
  python examples/evidence_run_logger.py log --domain distance_est --metrics '{"overall":0.65}'
  python examples/evidence_run_logger.py export-compare data/eval_compare_rebalance.json
  python examples/evidence_run_logger.py freeze --domain quantum_label --pct 90 \\
      --metrics-json data/eval_compare_rebalance.json --artifact data/lora_adapter_frozen_rebalance_20260924-041300
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOG = ROOT / "data" / "evidence_runs.jsonl"
FREEZE_DIR = ROOT / "data" / "freeze_manifests"
COMPARE_DIR = ROOT / "data" / "compare_tables"

# Required top-level fields for a complete evidence record.
SCHEMA_FIELDS = (
    "ts",
    "run_id",
    "domain",
    "metrics",
    "inputs",
    "outputs",
    "tool_calls",
    "retrieval_hits",
    "frames",
    "git_sha",
    "notes",
)


def _now_et() -> str:
    # Box/Mac lab clocks are America/New_York; label explicitly.
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " ET"


def git_sha(short: bool = True) -> str:
    try:
        args = ["git", "-C", str(ROOT), "rev-parse"]
        if short:
            args.append("--short")
        args.append("HEAD")
        out = subprocess.check_output(args, stderr=subprocess.DEVNULL, text=True).strip()
        return out or "UNKNOWN"
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return "UNKNOWN"


def new_run_id(domain: str) -> str:
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in domain)[:40]
    return f"{safe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def make_record(
    *,
    domain: str,
    metrics: dict[str, Any] | None = None,
    inputs: dict[str, Any] | None = None,
    outputs: dict[str, Any] | None = None,
    tool_calls: list[Any] | None = None,
    retrieval_hits: list[Any] | None = None,
    frames: list[str] | None = None,
    notes: str = "",
    run_id: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a complete evidence record (all SCHEMA_FIELDS present)."""
    rec: dict[str, Any] = {
        "ts": _now_et(),
        "run_id": run_id or new_run_id(domain),
        "domain": domain,
        "metrics": metrics or {},
        "inputs": inputs or {},
        "outputs": outputs or {},
        "tool_calls": tool_calls if tool_calls is not None else [],
        "retrieval_hits": retrieval_hits if retrieval_hits is not None else [],
        "frames": frames if frames is not None else [],
        "git_sha": git_sha(short=False),
        "notes": notes,
    }
    if extra:
        # Do not overwrite schema keys silently.
        for k, v in extra.items():
            if k not in rec:
                rec[k] = v
    return rec


def append_jsonl(record: dict[str, Any], path: Path | None = None) -> Path:
    path = path or DEFAULT_LOG
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path


def export_compare_table(
    compare_json: Path,
    *,
    out_dir: Path | None = None,
    prototype: dict[str, Any] | None = None,
    label: str | None = None,
) -> dict[str, Path]:
    """Export base vs adapter (finetuned) vs optional prototype as CSV + Markdown.

    Accepts eval_compare_*.json shape: {base, finetuned, delta, ...}
    or hybrid-style {own_delta_base_vs_ours, ...} — best-effort field pick.
    """
    out_dir = out_dir or COMPARE_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    data = json.loads(compare_json.read_text(encoding="utf-8"))
    stem = label or compare_json.stem
    base = data.get("base") or data.get("single_shot") or {}
    adapter = data.get("finetuned") or data.get("after_loop") or data.get("lora") or {}
    proto = prototype or data.get("prototype") or {}
    delta = data.get("delta") or data.get("delta_loop_minus_single") or data.get("own_delta_base_vs_ours") or {}

    # Metric keys = union of numeric-ish leaves at top level of each side.
    def flat_metrics(side: Any) -> dict[str, Any]:
        if not isinstance(side, dict):
            return {}
        out: dict[str, Any] = {}
        for k, v in side.items():
            if k in ("details", "adapter", "used_vlm"):
                continue
            if isinstance(v, (int, float, bool, str)):
                out[k] = v
        return out

    b_m, a_m, p_m, d_m = flat_metrics(base), flat_metrics(adapter), flat_metrics(proto), flat_metrics(delta)
    keys = sorted(set(b_m) | set(a_m) | set(p_m) | set(d_m))

    csv_path = out_dir / f"{stem}.csv"
    md_path = out_dir / f"{stem}.md"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["metric", "base", "adapter", "prototype", "delta"])
        for k in keys:
            w.writerow([k, b_m.get(k, ""), a_m.get(k, ""), p_m.get(k, ""), d_m.get(k, "")])

    lines = [
        f"# Compare table — `{stem}`",
        "",
        f"- source: `{compare_json}`",
        f"- exported: {_now_et()}",
        f"- git_sha: `{git_sha(short=False)}`",
        "",
        "| metric | base | adapter | prototype | delta |",
        "|--------|------|---------|-----------|-------|",
    ]
    for k in keys:
        lines.append(
            f"| {k} | {b_m.get(k, '')} | {a_m.get(k, '')} | {p_m.get(k, '')} | {d_m.get(k, '')} |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"csv": csv_path, "md": md_path}


def write_freeze_manifest(
    *,
    domain: str,
    pct: float,
    metrics: dict[str, Any] | None = None,
    artifact: str | None = None,
    eval_path: str | None = None,
    note: str = "",
    out_dir: Path | None = None,
) -> Path:
    """Freeze an 80/90/100% advance with git SHA (Plan Maestro §5.1.B).

    Writes data/freeze_manifests/<domain>_<pct>_<ts>.json — never touches adapters.
    """
    out_dir = out_dir or FREEZE_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    band = int(pct) if float(pct).is_integer() else pct
    ts_slug = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in domain)[:40]
    path = out_dir / f"{safe}_{band}pct_{ts_slug}.json"
    manifest = {
        "schema": "qlab_freeze_manifest_v1",
        "frozen_at_et": _now_et(),
        "domain": domain,
        "pct": float(pct),
        "band": "80" if pct < 85 else ("90" if pct < 95 else "100"),
        "git_sha": git_sha(short=False),
        "git_sha_short": git_sha(short=True),
        "artifact": artifact,
        "eval_path": eval_path,
        "metrics": metrics or {},
        "note": note or f"Freeze ~{band}% platform baseline (Plan Maestro §5.1.B).",
        "policy": "Do not abandon; polish and/or reinforce around. RO quantum adapters.",
    }
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    # Also append a one-line pointer into evidence_runs.jsonl
    append_jsonl(
        make_record(
            domain=domain,
            metrics={"freeze_pct": float(pct), **(metrics or {})},
            inputs={"artifact": artifact, "eval_path": eval_path},
            outputs={"freeze_manifest": str(path.relative_to(ROOT))},
            notes=f"freeze_manifest {band}%",
            extra={"kind": "freeze"},
        )
    )
    return path


def find_frames_for_seq(seq_id: str, roots: list[Path] | None = None) -> list[str]:
    """Best-effort: locate PNGs under known visual synth trees for a seq_id."""
    roots = roots or [
        ROOT / "data" / "video_synth" / "distance_est",
        ROOT / "data" / "video_synth" / "fase1",
        ROOT / "data" / "classical_scenes",
        ROOT / "data" / "experiment_scenes",
        ROOT / "data" / "inverse_planning",
    ]
    found: list[str] = []
    for root in roots:
        if not root.exists():
            continue
        # direct child named seq_id
        cand = root / seq_id
        if cand.is_dir():
            for p in sorted(cand.rglob("*.png"))[:32]:
                found.append(str(p.relative_to(ROOT)))
        # nested frames/
        for p in root.glob(f"**/{seq_id}/frames/*.png"):
            rel = str(p.relative_to(ROOT))
            if rel not in found:
                found.append(rel)
    return found[:48]


def cmd_demo(_: argparse.Namespace) -> int:
    """Smoke: write one synthetic record + export one existing compare if present."""
    frames = find_frames_for_seq("de_007_ash_ct")
    rec = make_record(
        domain="distance_est",
        metrics={"overall_correct": 0.6529, "note": "demo_only_not_a_real_rerun"},
        inputs={"seq_id": "de_007_ash_ct", "scale_lock": "FLOOR-SCALE"},
        outputs={"n_preds": 17},
        tool_calls=[{"tool": "floor_scale+parallax"}],
        retrieval_hits=[],
        frames=frames[:4],
        notes="evidence_run_logger demo — does not replace eval_audit writers",
    )
    path = append_jsonl(rec)
    print(f"WROTE {path}")
    print(json.dumps({k: rec[k] for k in SCHEMA_FIELDS}, indent=2)[:800])
    cmp = ROOT / "data" / "eval_compare_rebalance.json"
    if cmp.exists():
        paths = export_compare_table(cmp)
        print("EXPORTED", {k: str(v) for k, v in paths.items()})
    return 0


def cmd_log(args: argparse.Namespace) -> int:
    metrics = json.loads(args.metrics) if args.metrics else {}
    inputs = json.loads(args.inputs) if args.inputs else {}
    outputs = json.loads(args.outputs) if args.outputs else {}
    tools = json.loads(args.tool_calls) if args.tool_calls else []
    hits = json.loads(args.retrieval_hits) if args.retrieval_hits else []
    frames = list(args.frame or [])
    if args.seq_id and not frames:
        frames = find_frames_for_seq(args.seq_id)
        inputs.setdefault("seq_id", args.seq_id)
    rec = make_record(
        domain=args.domain,
        metrics=metrics,
        inputs=inputs,
        outputs=outputs,
        tool_calls=tools,
        retrieval_hits=hits,
        frames=frames,
        notes=args.notes or "",
    )
    path = append_jsonl(rec, Path(args.out) if args.out else None)
    print(path)
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    proto = json.loads(args.prototype) if args.prototype else None
    paths = export_compare_table(Path(args.compare_json), prototype=proto, label=args.label)
    print(json.dumps({k: str(v) for k, v in paths.items()}, indent=2))
    return 0


def cmd_freeze(args: argparse.Namespace) -> int:
    metrics: dict[str, Any] = {}
    eval_path = args.metrics_json
    if args.metrics_json:
        raw = json.loads(Path(args.metrics_json).read_text(encoding="utf-8"))
        # Prefer top-level finetuned / result / overall
        if isinstance(raw, dict):
            if "result" in raw and isinstance(raw["result"], dict):
                metrics = dict(raw["result"])
            elif "finetuned" in raw and isinstance(raw["finetuned"], dict):
                metrics = {
                    k: v
                    for k, v in raw["finetuned"].items()
                    if isinstance(v, (int, float, bool, str))
                }
            else:
                metrics = {
                    k: v for k, v in raw.items() if isinstance(v, (int, float, bool, str))
                }
    if args.metrics:
        metrics.update(json.loads(args.metrics))
    path = write_freeze_manifest(
        domain=args.domain,
        pct=float(args.pct),
        metrics=metrics,
        artifact=args.artifact,
        eval_path=eval_path,
        note=args.note or "",
    )
    print(path)
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="QLab evidence run logger (stdlib)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_demo = sub.add_parser("demo", help="Write one demo evidence line + export compare if present")
    p_demo.set_defaults(func=cmd_demo)

    p_log = sub.add_parser("log", help="Append one evidence JSONL record")
    p_log.add_argument("--domain", required=True)
    p_log.add_argument("--metrics", default="{}")
    p_log.add_argument("--inputs", default="{}")
    p_log.add_argument("--outputs", default="{}")
    p_log.add_argument("--tool-calls", default="[]")
    p_log.add_argument("--retrieval-hits", default="[]")
    p_log.add_argument("--frame", action="append", default=[])
    p_log.add_argument("--seq-id", default=None)
    p_log.add_argument("--notes", default="")
    p_log.add_argument("--out", default=None)
    p_log.set_defaults(func=cmd_log)

    p_ex = sub.add_parser("export-compare", help="CSV+MD base/adapter/prototype table")
    p_ex.add_argument("compare_json")
    p_ex.add_argument("--prototype", default=None, help="JSON object for prototype column")
    p_ex.add_argument("--label", default=None)
    p_ex.set_defaults(func=cmd_export)

    p_fr = sub.add_parser("freeze", help="Write §5.1.B freeze manifest with git SHA")
    p_fr.add_argument("--domain", required=True)
    p_fr.add_argument("--pct", required=True, type=float)
    p_fr.add_argument("--metrics-json", default=None, help="Path to eval JSON to mine metrics from")
    p_fr.add_argument("--metrics", default=None, help="Inline JSON metrics override/merge")
    p_fr.add_argument("--artifact", default=None)
    p_fr.add_argument("--note", default="")
    p_fr.set_defaults(func=cmd_freeze)

    args = ap.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    # Refuse to run if somehow pointed at adapter mutation — logger is append-only files.
    if os.environ.get("QLAB_EVIDENCE_TOUCH_ADAPTER") == "1":
        print("Refusing: evidence logger must not mutate adapters", file=sys.stderr)
        sys.exit(2)
    raise SystemExit(main())
