from __future__ import annotations

import random
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from .registry import ToolRegistry
from .run_step_v2 import run_step_v2

JSON = Dict[str, Any]


def _rid() -> str:
    return uuid.uuid4().hex[:12]


def train_loop_v1(
    reg: ToolRegistry,
    *,
    steps: int,
    out_dir: Path,
    seed: int = 0,
    run_id: Optional[str] = None,
) -> JSON:
    run_id = run_id or f"train-{_rid()}"
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    rng = random.Random(int(seed))
    workspace = out_dir / "workspace.blend"
    snaps = out_dir / "snaps"

    history: List[JSON] = []
    total = 0.0

    for i in range(int(steps)):
        name = f"ATLAS_Train_Cube_{i:04d}"
        loc = {
            "x": round(rng.uniform(-3.0, 3.0), 3),
            "y": round(rng.uniform(-3.0, 3.0), 3),
            "z": round(rng.uniform(0.0, 2.0), 3),
        }

        s = run_step_v2(
            reg,
            action_tool="atlas.blender.add_cube_v1",
            action_args={"name": name, "location": loc},
            snapshot_out_dir=snaps,
            run_id=f"{run_id}-{i+1:04d}",
            workspace_blend_path=workspace,
        )
        total += float(s.get("score", 0.0))
        history.append({"run_id": s["run_id"], "score": s["score"], "diff_counts": s["diff"]["counts"]})

    return {
        "schema": "atlas.train.loop.v1",
        "run_id": run_id,
        "seed": int(seed),
        "steps": int(steps),
        "workspace_blend": str(workspace),
        "history": history,
        "total_score": float(total),
        "avg_score": float(total / max(int(steps), 1)),
        "out_dir": str(out_dir),
    }
