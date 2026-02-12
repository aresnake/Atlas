from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from .registry import ToolRegistry
from .run_step import run_step_v1

JSON = Dict[str, Any]


def _rid() -> str:
    return uuid.uuid4().hex[:12]


def benchmark_smoke_v1(
    reg: ToolRegistry,
    *,
    out_dir: Path,
    run_id: Optional[str] = None,
) -> JSON:
    run_id = run_id or f"smoke-{_rid()}"
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    workspace = out_dir / "workspace.blend"
    snaps = out_dir / "snaps"

    steps: List[JSON] = []

    steps.append(
        run_step_v1(
            reg,
            action_tool="atlas.blender.add_cube_v1",
            action_args={"name": "ATLAS_Bench_Cube_A", "location": {"x": 0.0, "y": 0.0, "z": 0.0}},
            snapshot_out_dir=snaps,
            run_id=f"{run_id}-01",
            workspace_blend_path=workspace,
        )
    )

    steps.append(
        run_step_v1(
            reg,
            action_tool="atlas.blender.add_cube_v1",
            action_args={"name": "ATLAS_Bench_Cube_B", "location": {"x": 2.0, "y": 0.0, "z": 0.0}},
            snapshot_out_dir=snaps,
            run_id=f"{run_id}-02",
            workspace_blend_path=workspace,
        )
    )

    steps.append(
        run_step_v1(
            reg,
            action_tool="atlas.ping",
            action_args={},
            snapshot_out_dir=snaps,
            run_id=f"{run_id}-03",
            workspace_blend_path=workspace,
        )
    )

    total = sum(float(s.get("score", 0.0)) for s in steps)

    return {
        "schema": "atlas.benchmark.smoke.v1",
        "run_id": run_id,
        "workspace_blend": str(workspace),
        "steps": [{"run_id": s["run_id"], "score": s["score"], "diff_counts": s["diff"]["counts"]} for s in steps],
        "total_score": float(total),
    }
