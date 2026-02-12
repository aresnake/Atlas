from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .registry import ToolRegistry, json_result
from .run_step_v2 import run_step_v2

JSON = Dict[str, Any]


def register_run_tools(reg: ToolRegistry) -> ToolRegistry:
    # keep v1 if you want (already exists elsewhere) — but we register v2 here
    reg.register(
        {
            "name": "atlas.run.step_v2",
            "description": "Run one training step v2: snapshot_v2 -> action -> snapshot_v2 -> diff_v2 -> score_v2 -> jsonl log",
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
            run_step_v2(
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
