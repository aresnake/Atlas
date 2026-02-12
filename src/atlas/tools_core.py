from __future__ import annotations

from typing import Any, Dict

from .registry import ToolRegistry, text_result, json_result
from .tools_blender import register_blender_tools
from .tools_diff import register_diff_tools
from .tools_run_v2 import register_run_tools
from .tools_train import register_train_tools

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

    register_diff_tools(reg)
    register_blender_tools(reg)
    register_run_tools(reg)      # v2
    register_train_tools(reg)    # loop v1

    return reg
