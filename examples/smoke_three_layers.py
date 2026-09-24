#!/usr/bin/env python3
"""CPU smoke: WorkingMemory → RetrievalIndex (train-only) → TrafficPhysicsTool.
No VLM/GPU. Anti-contam: query uses memory features only; index is train split.
"""
from __future__ import annotations
import json, sys, importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
F1 = ROOT / "data" / "video_synth" / "fase1"


def _load():
    name = "video_temporal_prototype"
    path = ROOT / "examples" / "video_temporal_prototype.py"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    vtp = _load()
    split = json.loads((F1 / "split.json").read_text(encoding="utf-8"))
    train_ids = split["train_ids"]
    eval_ids = set(split["eval_ids"])
    idx = vtp.RetrievalIndex()
    idx.build_from_train([F1 / s for s in train_ids])
    idx.set_eval_ids(eval_ids)

    mem = vtp.WorkingMemory()
    mem.update_from_perception(
        {
            "street_name": "Oak Ave",
            "tracks": [
                {"id": "L0", "class": "light", "state": "G", "frames": [{"x": 10, "y": 20}, {"x": 10, "y": 20}]},
                {"id": "C0", "class": "car", "color": "red", "frames": [{"x": 100, "y": 200}, {"x": 108, "y": 200}]},
                {"id": "P0", "class": "pedestrian", "frames": [{"x": 50, "y": 180}, {"x": 52, "y": 180}]},
            ],
            "relations": ["car approaching light"],
        }
    )
    hit = idx.query(mem)
    assert hit and hit["hit_seq_id"] in idx.train_ids and hit["hit_seq_id"] not in idx.eval_ids
    tool = vtp.TrafficPhysicsTool()
    out = tool.run(mem)
    mem.update_from_tool(out)
    report = {
        "ok": True,
        "index_n": len(idx.entries),
        "retrieval_hit": {
            "hit_seq_id": hit["hit_seq_id"],
            "distance": hit.get("distance"),
            "query_features": hit.get("query_features"),
        },
        "memory_snapshot": mem.snapshot(),
        "tool": {"note": out.get("note"), "light_next": out.get("light_next"), "source": out.get("source")},
        "packages": ["stdlib", "numpy"],
        "not_required": ["faiss", "chromadb", "sentence_transformers"],
    }
    out_path = F1 / "SMOKE_THREE_LAYERS.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print("WROTE", out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
