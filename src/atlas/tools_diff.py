from __future__ import annotations

import json
from typing import Any, Dict

from .registry import ToolRegistry, json_result
from .snapshot_diff import diff_snapshot_v1

JSON = Dict[str, Any]


def register_diff_tools(reg: ToolRegistry) -> ToolRegistry:
    reg.register(
        {
            "name": "atlas.snapshot.diff_v1",
            "description": "Diff two atlas.snapshot.v1 JSON objects; returns atlas.snapshot.diff.v1",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "a": {"type": "object"},
                    "b": {"type": "object"},
                },
                "required": ["a", "b"],
                "additionalProperties": False,
            },
        },
        lambda args: json_result(diff_snapshot_v1(args["a"], args["b"])),
    )
    return reg
