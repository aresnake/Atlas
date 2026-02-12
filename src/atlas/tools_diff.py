from __future__ import annotations

from typing import Any, Dict

from .registry import ToolRegistry, json_result
from .snapshot_diff import diff_snapshot_v1
from .snapshot_diff_v2 import diff_snapshot_v2

JSON = Dict[str, Any]


def register_diff_tools(reg: ToolRegistry) -> ToolRegistry:
    reg.register(
        {
            "name": "atlas.snapshot.diff_v1",
            "description": "Diff two atlas.snapshot.v1 JSON objects; returns atlas.snapshot.diff.v1",
            "inputSchema": {
                "type": "object",
                "properties": {"a": {"type": "object"}, "b": {"type": "object"}},
                "required": ["a", "b"],
                "additionalProperties": False,
            },
        },
        lambda args: json_result(diff_snapshot_v1(args["a"], args["b"])),
    )

    reg.register(
        {
            "name": "atlas.snapshot.diff_v2",
            "description": "Diff two atlas.snapshot.v2 JSON objects; returns atlas.snapshot.diff.v2 (object fingerprints).",
            "inputSchema": {
                "type": "object",
                "properties": {"a": {"type": "object"}, "b": {"type": "object"}},
                "required": ["a", "b"],
                "additionalProperties": False,
            },
        },
        lambda args: json_result(diff_snapshot_v2(args["a"], args["b"])),
    )

    return reg
