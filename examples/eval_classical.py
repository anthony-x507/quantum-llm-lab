#!/usr/bin/env python3
"""
Eval classical lane: emitted Python must execute AND match GT within tolerance.

Also optional READ-ONLY transfer test: run quantum adapter on classical set
(expect poor transfer — report honestly).

  python examples/eval_classical.py --adapter data/lora_adapter_classical --n-test 30
  python examples/eval_classical.py --adapter data/lora_adapter_classical \
      --quantum-adapter data/lora_adapter --n-test 20
"""

from __future__ import annotations

import argparse
import io
import json
import random
import re
import sys
from collections import defaultdict
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "examples"))

from train_lora_classical import (  # noqa: E402
    _user_prompt,
    load_classical_scenes,
)


def _strip_thinking(text: str) -> str:
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r"<thinking>.*?</thinking>", "", cleaned, flags=re.IGNORECASE | re.DOTALL)
    # strip markdown fences if model wraps code
    cleaned = re.sub(r"^```(?:python)?\s*", "", cleaned.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned.strip())
    return cleaned.strip()


def _extract_python(text: str) -> str:
    t = _strip_thinking(text)
    # if still has fence inside
    m = re.search(r"```(?:python)?\s*([\s\S]*?)```", t, flags=re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return t


def exec_metrics(src: str, timeout_s: float = 2.0) -> dict[str, float] | None:
    """Exec python source; parse last printed dict with required keys."""
    if not src or "import os" in src or "open(" in src or "subprocess" in src:
        # soft refuse dangerous — still try if just math
        if any(x in src for x in ("subprocess", "socket", "requests", "__import__('os')")):
            return None
    try:
        buf = io.StringIO()
        ns: dict[str, Any] = {"__name__": "__main__"}
        with redirect_stdout(buf):
            exec(compile(src, "<pred>", "exec"), ns, ns)
        text = buf.getvalue().strip()
        if not text:
            return None
        last = text.splitlines()[-1]
        pred = eval(last, {"__builtins__": {}}, {})
        if not isinstance(pred, dict):
            return None
        out = {}
        for k in ("range_m", "max_height_m", "impact_speed_m_s"):
            if k not in pred:
                return None
            out[k] = float(pred[k])
        return out
    except Exception:
        return None


def within_tol(pred: dict[str, float], gold: dict[str, float], tol: dict[str, float]) -> bool:
    for k in ("range_m", "max_height_m", "impact_speed_m_s"):
        if abs(pred[k] - float(gold[k])) > float(tol[k]) + 1e-9:
            return False
    return True


def evaluate(
    rows: list[dict[str, Any]],
    *,
    model_id: str,
    adapter: str | None,
    n_test: int,
    seed: int,
    label: str,
) -> dict[str, Any]:
    rng = random.Random(seed)
    # stratify by subdomain
    by: dict[str, list] = defaultdict(list)
    for r in rows:
        by[str(r["meta"].get("subdomain") or "other")].append(r)
    for v in by.values():
        rng.shuffle(v)
    sample: list[dict[str, Any]] = []
    subs = sorted(by.keys())
    if not subs:
        return {"n": 0, "exec_rate": 0.0, "match_rate": 0.0, "label": label}
    # round-robin
    while len(sample) < min(n_test, len(rows)):
        progress = False
        for s in subs:
            if by[s] and len(sample) < n_test:
                sample.append(by[s].pop())
                progress = True
        if not progress:
            break
    rng.shuffle(sample)

    use_vlm = False
    model = processor = config = None
    try:
        from mlx_vlm import load, generate
        from mlx_vlm.prompt_utils import apply_chat_template
        from mlx_vlm.utils import load_config

        kwargs = {"adapter_path": adapter} if adapter else {}
        print(f"[{label}] Cargando VLM {model_id} adapter={adapter!r} …", flush=True)
        model, processor = load(model_id, **kwargs)
        config = load_config(model_id)
        use_vlm = True
    except Exception as exc:  # noqa: BLE001
        print(f"[{label}] VLM unavailable ({exc}); gold-python dry-run only.", file=sys.stderr)

    exec_ok = match_ok = 0
    by_sub_stats: dict[str, dict[str, int]] = defaultdict(lambda: {"n": 0, "exec": 0, "match": 0})
    details: list[dict[str, Any]] = []

    for row in sample:
        meta = row["meta"]
        sub = str(meta.get("subdomain") or "other")
        by_sub_stats[sub]["n"] += 1
        gold = meta.get("expected_metrics") or {}
        tol = meta.get("tolerance") or {}
        source = "gold_dry"
        raw_text = ""
        if use_vlm and model is not None:
            prompt = _user_prompt(meta)
            image = row.get("frame_path")
            formatted = apply_chat_template(
                processor, config, prompt, num_images=1 if image else 0
            )
            try:
                result = generate(
                    model, processor, formatted, image=image, max_tokens=768, verbose=False
                )
                raw_text = result.text if hasattr(result, "text") else str(result)
                src = _extract_python(raw_text)
                source = "vlm"
            except Exception as exc:  # noqa: BLE001
                details.append(
                    {
                        "scene_id": row["scene_id"],
                        "subdomain": sub,
                        "source": f"fail:{type(exc).__name__}",
                        "error": str(exc)[:200],
                        "exec": False,
                        "match": False,
                    }
                )
                continue
        else:
            src = row.get("target_python") or meta.get("gold_python") or ""

        pred = exec_metrics(src)
        ok_e = pred is not None
        ok_m = bool(ok_e and within_tol(pred, gold, tol))  # type: ignore[arg-type]
        if ok_e:
            exec_ok += 1
            by_sub_stats[sub]["exec"] += 1
        if ok_m:
            match_ok += 1
            by_sub_stats[sub]["match"] += 1
        details.append(
            {
                "scene_id": row["scene_id"],
                "subdomain": sub,
                "source": source,
                "exec": ok_e,
                "match": ok_m,
                "pred": pred,
                "gold": {k: gold.get(k) for k in ("range_m", "max_height_m", "impact_speed_m_s")},
            }
        )

    n = max(1, len(sample))
    breakdown = {}
    for s, st in sorted(by_sub_stats.items()):
        nn = max(1, st["n"])
        breakdown[s] = {
            "n": st["n"],
            "exec_rate": st["exec"] / nn,
            "match_rate": st["match"] / nn,
        }
    return {
        "label": label,
        "n": len(sample),
        "exec_rate": exec_ok / n,
        "match_rate": match_ok / n,
        "used_vlm": use_vlm,
        "adapter": adapter,
        "by_subdomain": breakdown,
        "details": details,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Eval classical image→Python→metrics")
    ap.add_argument("--model", default="mlx-community/Qwen3-VL-8B-Thinking-4bit")
    ap.add_argument("--adapter", type=Path, default=ROOT / "data" / "lora_adapter_classical")
    ap.add_argument(
        "--quantum-adapter",
        type=Path,
        default=None,
        help="READ-ONLY quantum adapter for transfer compare",
    )
    ap.add_argument("--scenes", type=Path, default=ROOT / "data" / "classical_scenes")
    ap.add_argument("--n-test", type=int, default=24)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--gold-dry", action="store_true", help="Skip VLM; verify gold python only")
    args = ap.parse_args()

    rows = load_classical_scenes(args.scenes)
    if not rows:
        print(f"No classical scenes in {args.scenes}", file=sys.stderr)
        return 1

    # Always run gold dry sanity (CPU only — never loads VLM)
    print("=== GOLD PYTHON SANITY (CPU) ===", flush=True)
    g_ok = g_match = 0
    by_sub: dict[str, dict[str, int]] = {}
    sample_n = min(args.n_test, len(rows)) if args.gold_dry else min(args.n_test, len(rows))
    # For --gold-dry verify ALL scenes; else a sample
    if args.gold_dry:
        sample = rows
    else:
        rng = random.Random(args.seed)
        sample = rows[:] if len(rows) <= sample_n else rng.sample(rows, sample_n)
    for row in sample:
        meta = row["meta"]
        sub = str(meta.get("subdomain") or "?")
        by_sub.setdefault(sub, {"n": 0, "exec": 0, "match": 0})
        by_sub[sub]["n"] += 1
        pred = exec_metrics(row.get("target_python") or meta.get("gold_python") or "")
        if pred:
            g_ok += 1
            by_sub[sub]["exec"] += 1
            if within_tol(pred, meta["expected_metrics"], meta["tolerance"]):
                g_match += 1
                by_sub[sub]["match"] += 1
    breakdown = {
        s: {
            "n": st["n"],
            "exec_rate": st["exec"] / max(1, st["n"]),
            "match_rate": st["match"] / max(1, st["n"]),
        }
        for s, st in sorted(by_sub.items())
    }
    gold_report = {
        "n": len(sample),
        "exec_rate": g_ok / max(1, len(sample)),
        "match_rate": g_match / max(1, len(sample)),
        "by_subdomain": breakdown,
        "used_vlm": False,
    }
    print(json.dumps(gold_report, indent=2))

    report: dict[str, Any] = {"gold_python_sanity": gold_report, "lane": "classical"}

    if args.gold_dry:
        out = args.out or (ROOT / "data" / "BENCHMARK_CLASSICAL.json")
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {out}")
        return 0 if gold_report["match_rate"] >= 0.99 else 2

    # Classical adapter (if present)
    ft = None
    if args.adapter.exists() and (
        (args.adapter / "adapters.safetensors").exists()
        or any(args.adapter.glob("*.safetensors"))
    ):
        print("=== CLASSICAL ADAPTER ===", flush=True)
        ft = evaluate(
            rows,
            model_id=args.model,
            adapter=str(args.adapter),
            n_test=args.n_test,
            seed=args.seed,
            label="classical_lora",
        )
        print(
            json.dumps(
                {k: ft[k] for k in ("n", "exec_rate", "match_rate", "by_subdomain", "used_vlm")},
                indent=2,
            )
        )
    else:
        print(f"[warn] Classical adapter not ready at {args.adapter}", file=sys.stderr)

    # Base (no adapter)
    print("=== BASE (no adapter) ===", flush=True)
    base = evaluate(
        rows,
        model_id=args.model,
        adapter=None,
        n_test=args.n_test,
        seed=args.seed,
        label="base",
    )
    print(
        json.dumps(
            {k: base[k] for k in ("n", "exec_rate", "match_rate", "by_subdomain", "used_vlm")},
            indent=2,
        )
    )

    q_transfer = None
    qpath = args.quantum_adapter
    if qpath is None:
        qpath = ROOT / "data" / "lora_adapter"
    if qpath.exists() and (qpath / "adapters.safetensors").exists():
        print("=== QUANTUM ADAPTER (READ-ONLY transfer on classical) ===", flush=True)
        q_transfer = evaluate(
            rows,
            model_id=args.model,
            adapter=str(qpath),
            n_test=args.n_test,
            seed=args.seed,
            label="quantum_transfer",
        )
        print(
            json.dumps(
                {
                    k: q_transfer[k]
                    for k in ("n", "exec_rate", "match_rate", "by_subdomain", "used_vlm")
                },
                indent=2,
            )
        )
        print(
            "Transfer note: expect poor transfer (quantum circuits ≠ classical Python). "
            "Report honestly — no quantum-advantage claims.",
            flush=True,
        )

    report.update({"base": base, "classical_lora": ft, "quantum_transfer_readonly": q_transfer})
    if ft and base:
        report["delta_match"] = ft["match_rate"] - base["match_rate"]
    if q_transfer and ft:
        report["classical_vs_quantum_transfer"] = {
            "classical_match": ft["match_rate"],
            "quantum_on_classical_match": q_transfer["match_rate"],
            "note": "Expect classical adapter >> quantum adapter on this set (different target language).",
        }

    out = args.out or (ROOT / "data" / "BENCHMARK_CLASSICAL.json")
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
