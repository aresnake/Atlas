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

    reg.register(
        {
            "name": "atlas.blender.add_cube_v1",
            "description": "Create a cube data-first (no context). Returns atlas.blender.add_cube.v1",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "location": {"type": "object"},
                },
                "required": ["name", "location"],
                "additionalProperties": False,
            },
        },
        lambda args: json_result(
            run_blender_script(
                Path("tools/blender_add_cube_v1.py"),
                extra_args=[
                    "--name", str(args["name"]),
                    "--location",
                    str(args["location"].get("x", 0.0)),
                    str(args["location"].get("y", 0.0)),
                    str(args["location"].get("z", 0.0)),
                ],
            )
        ),
    )

    return reg
