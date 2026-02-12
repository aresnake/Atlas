from __future__ import annotations

from typing import Dict, Any

from .registry import ToolRegistry, text_result, json_result
from .tools_blender import register_blender_tools

JSON = Dict[str, Any]


def build_registry() -> ToolRegistry:
    reg = ToolRegistry()

    reg.register(
        {
            "name": "atlas.ping",
            "description": "Health check. Returns 'pong'.",
            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        },
        lambda args: text_result("pong"),
    )

    reg.register(
        {
            "name": "atlas.echo",
            "description": "Echo back provided text.",
            "inputSchema": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
                "additionalProperties": False,
            },
        },
        lambda args: json_result({"echo": args["text"]}),
    )

    # Blender tools (may require env ATLAS_BLENDER_EXE)
    register_blender_tools(reg)

    return reg
