from __future__ import annotations

from pathlib import Path
from typing import Dict, Any

from .registry import ToolRegistry, json_result
from .blender_backend import run_blender_script

JSON = Dict[str, Any]


def register_blender_tools(reg: ToolRegistry) -> ToolRegistry:
    reg.register(
        {
            "name": "atlas.blender.snapshot_v1",
            "description": "Headless Blender snapshot (scenegraph) schema atlas.snapshot.v1",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "out_path": {"type": "string"},
                },
                "required": ["out_path"],
                "additionalProperties": False,
            },
        },
        lambda args: json_result(
            run_blender_script(
                Path("tools/blender_snapshot_v1.py"),
                out_json_path=Path(args["out_path"]),
            )
        ),
    )
    return reg
