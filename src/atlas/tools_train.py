from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .registry import ToolRegistry, json_result
from .train_loop import train_loop_v1

JSON = Dict[str, Any]


def register_train_tools(reg: ToolRegistry) -> ToolRegistry:
    reg.register(
        {
            "name": "atlas.train.loop_v1",
            "description": "Run N deterministic training steps (add_cube policy) and write dataset JSONL.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "steps": {"type": "integer"},
                    "out_dir": {"type": "string"},
                    "run_id": {"type": "string"},
                },
                "required": ["steps", "out_dir"],
                "additionalProperties": False,
            },
        },
        lambda args: json_result(
            train_loop_v1(
                reg,
                steps=int(args["steps"]),
                out_dir=Path(args["out_dir"]),
                run_id=args.get("run_id"),
            )
        ),
    )
    return reg
