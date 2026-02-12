from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from .registry import ToolRegistry
from .run_step import run_step_v1

JSON = Dict[str, Any]


def _rid() -> str:
    return uuid.uuid4().hex[:12]


def _policy_add_cube(i: int) -> JSON:
    # Deterministic grid policy (v1)
    x = float((i % 5) * 2)
    y = float((i // 5) * 2)
    return {
        "tool": "atlas.blender.add_cube_v1",
        "args": {
            "name": f"ATLAS_Train_Cube_{i:04d}",
            "location": {"x": x, "y": y, "z": 0.0},
        },
    }


def train_loop_v1(
    reg: ToolRegistry,
    *,
    steps: int,
    out_dir: Path,
    run_id: Optional[str] = None,
) -> JSON:
    if steps <= 0:
        raise ValueError("steps must be > 0")

    run_id = run_id or f"train-{_rid()}"
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    workspace = out_dir / "workspace.blend"
    snaps = out_dir / "snaps"
    dataset_path = out_dir / "train_loop.jsonl"

    rows: List[JSON] = []
    total_score = 0.0

    for i in range(steps):
        policy = _policy_add_cube(i)
        step_run_id = f"{run_id}-{i+1:04d}"

        step = run_step_v1(
            reg,
            action_tool=policy["tool"],
            action_args=policy["args"],
            snapshot_out_dir=snaps,
            run_id=step_run_id,
            workspace_blend_path=workspace,
        )

        total_score += float(step.get("score", 0.0))

        row = {
            "schema": "atlas.train.row.v1",
            "run_id": run_id,
            "step_index": i,
            "step_run_id": step_run_id,
            "action": step["action"],
            "diff": step["diff"],
            "score": step["score"],
            "paths": step["paths"],
        }
        rows.append(row)

    with dataset_path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    return {
        "schema": "atlas.train.loop.v1",
        "run_id": run_id,
        "steps": steps,
        "total_score": float(total_score),
        "avg_score": float(total_score / steps),
        "workspace_blend": str(workspace),
        "dataset_jsonl": str(dataset_path),
        "snaps_dir": str(snaps),
    }
