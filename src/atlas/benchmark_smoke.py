from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from .contract import AtlasError
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

    # 3 deterministic steps
    steps: List[JSON] = []

    # Step 1: add cube
    steps.append(
        run_step_v1(
            reg,
            action_tool="atlas.blender.add_cube_v1",
            action_args={"name": "ATLAS_Bench_Cube_A", "location": {"x": 0.0, "y": 0.0, "z": 0.0}},
            snapshot_out_dir=out_dir / "snaps",
            run_id=f"{run_id}-01",
        )
    )

    # Step 2: add cube
    steps.append(
        run_step_v1(
            reg,
            action_tool="atlas.blender.add_cube_v1",
            action_args={"name": "ATLAS_Bench_Cube_B", "location": {"x": 2.0, "y": 0.0, "z": 0.0}},
            snapshot_out_dir=out_dir / "snaps",
            run_id=f"{run_id}-02",
        )
    )

    # Step 3: ping (no scene change expected)
    steps.append(
        run_step_v1(
            reg,
            action_tool="atlas.ping",
            action_args={},
            snapshot_out_dir=out_dir / "snaps",
            run_id=f"{run_id}-03",
        )
    )

    total = sum(float(s.get("score", 0.0)) for s in steps)

    return {
        "schema": "atlas.benchmark.smoke.v1",
        "run_id": run_id,
        "steps": [{"run_id": s["run_id"], "score": s["score"], "diff_counts": s["diff"]["counts"]} for s in steps],
        "total_score": float(total),
    }
