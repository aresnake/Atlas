from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .registry import ToolRegistry, json_result
from .benchmark_smoke import benchmark_smoke_v1

JSON = Dict[str, Any]


def register_benchmark_tools(reg: ToolRegistry) -> ToolRegistry:
    reg.register(
        {
            "name": "atlas.benchmark.smoke_v1",
            "description": "Run 3-step smoke benchmark (2 cube adds + ping). Returns summary JSON.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "out_dir": {"type": "string"},
                    "run_id": {"type": "string"},
                },
                "required": ["out_dir"],
                "additionalProperties": False,
            },
        },
        lambda args: json_result(
            benchmark_smoke_v1(
                reg,
                out_dir=Path(args["out_dir"]),
                run_id=args.get("run_id"),
            )
        ),
    )
    return reg
