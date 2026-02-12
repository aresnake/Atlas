from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .registry import ToolRegistry, json_result
from .run_step import run_step_v1

JSON = Dict[str, Any]


def register_run_tools(reg: ToolRegistry) -> ToolRegistry:
    reg.register(
        {
            "name": "atlas.run.step_v1",
            "description": "Run one training step: snapshot_before -> action -> snapshot_after -> diff -> score -> jsonl log",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "action_tool": {"type": "string"},
                    "action_args": {"type": "object"},
                    "snapshot_out_dir": {"type": "string"},
                    "run_id": {"type": "string"},
                    "workspace_blend_path": {"type": "string"},
                },
                "required": ["action_tool", "action_args", "snapshot_out_dir"],
                "additionalProperties": False,
            },
        },
        lambda args: json_result(
            run_step_v1(
                reg,
                action_tool=args["action_tool"],
                action_args=args["action_args"],
                snapshot_out_dir=Path(args["snapshot_out_dir"]),
                run_id=args.get("run_id"),
                workspace_blend_path=Path(args["workspace_blend_path"]) if args.get("workspace_blend_path") else None,
            )
        ),
    )
    return reg
