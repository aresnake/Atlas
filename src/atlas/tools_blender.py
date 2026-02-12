from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .registry import ToolRegistry, json_result
from .blender_backend import run_blender_script

JSON = Dict[str, Any]


def _blend_arg(args: JSON) -> List[str]:
    bp = args.get("blend_path")
    if not bp:
        return []
    return ["--blend", str(bp)]


def register_blender_tools(reg: ToolRegistry) -> ToolRegistry:
    # init workspace
    reg.register(
        {
            "name": "atlas.blender.init_empty_v1",
            "description": "Create an empty .blend workspace (headless) at blend_path.",
            "inputSchema": {
                "type": "object",
                "properties": {"blend_path": {"type": "string"}},
                "required": ["blend_path"],
                "additionalProperties": False,
            },
        },
        lambda args: json_result(
            run_blender_script(
                Path("tools/blender_init_empty_v1.py"),
                extra_args=["--blend", str(args["blend_path"])],
            )
        ),
    )

    # snapshot v1 (kept)
    reg.register(
        {
            "name": "atlas.blender.snapshot_v1",
            "description": "Headless Blender snapshot (scenegraph) schema atlas.snapshot.v1",
            "inputSchema": {
                "type": "object",
                "properties": {"out_path": {"type": "string"}, "blend_path": {"type": "string"}},
                "required": ["out_path"],
                "additionalProperties": False,
            },
        },
        lambda args: json_result(
            run_blender_script(
                Path("tools/blender_snapshot_v1.py"),
                out_json_path=Path(args["out_path"]),
                extra_args=_blend_arg(args),
            )
        ),
    )

    # snapshot v2 (NEW)
    reg.register(
        {
            "name": "atlas.blender.snapshot_v2",
            "description": "Headless Blender snapshot schema atlas.snapshot.v2 (bbox/materials/collections/mesh_stats).",
            "inputSchema": {
                "type": "object",
                "properties": {"out_path": {"type": "string"}, "blend_path": {"type": "string"}},
                "required": ["out_path"],
                "additionalProperties": False,
            },
        },
        lambda args: json_result(
            run_blender_script(
                Path("tools/blender_snapshot_v2.py"),
                out_json_path=Path(args["out_path"]),
                extra_args=_blend_arg(args),
            )
        ),
    )

    # add cube
    reg.register(
        {
            "name": "atlas.blender.add_cube_v1",
            "description": "Create a cube data-first (no context). Optionally persists into blend_path.",
            "inputSchema": {
                "type": "object",
                "properties": {"name": {"type": "string"}, "location": {"type": "object"}, "blend_path": {"type": "string"}},
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
                    str((args["location"] or {}).get("x", 0.0)),
                    str((args["location"] or {}).get("y", 0.0)),
                    str((args["location"] or {}).get("z", 0.0)),
                    *_blend_arg(args),
                ],
            )
        ),
    )

    return reg
