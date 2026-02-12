from __future__ import annotations

import json
from typing import Any, Callable, Dict, List

from .contract import AtlasError, ToolResult, ToolSpec

JSON = Dict[str, Any]
Handler = Callable[[JSON], ToolResult]


def _is_object(x: Any) -> bool:
    return isinstance(x, dict)


def validate_against_schema(args: JSON, schema: JSON) -> None:
    # v0.1: minimal JSONSchema subset: type=object, properties, required, additionalProperties
    if schema.get("type") != "object":
        raise AtlasError("INVALID_ARGUMENTS", "inputSchema must be type=object")
    if not _is_object(args):
        raise AtlasError("INVALID_ARGUMENTS", "arguments must be an object")

    props = schema.get("properties") or {}
    required = schema.get("required") or []
    addl = schema.get("additionalProperties", True)

    for k in required:
        if k not in args:
            raise AtlasError("INVALID_ARGUMENTS", f"Missing required field: {k}")

    if addl is False:
        for k in args.keys():
            if k not in props:
                raise AtlasError("INVALID_ARGUMENTS", f"Unexpected field: {k}")

    # basic type checks
    for k, spec in props.items():
        if k not in args:
            continue
        expected = spec.get("type")
        v = args[k]
        if expected == "string" and not isinstance(v, str):
            raise AtlasError("INVALID_ARGUMENTS", f"Field '{k}' must be string")
        if expected == "number" and not isinstance(v, (int, float)):
            raise AtlasError("INVALID_ARGUMENTS", f"Field '{k}' must be number")
        if expected == "integer" and not isinstance(v, int):
            raise AtlasError("INVALID_ARGUMENTS", f"Field '{k}' must be integer")
        if expected == "boolean" and not isinstance(v, bool):
            raise AtlasError("INVALID_ARGUMENTS", f"Field '{k}' must be boolean")
        if expected == "object" and not _is_object(v):
            raise AtlasError("INVALID_ARGUMENTS", f"Field '{k}' must be object")


class ToolRegistry:
    def __init__(self) -> None:
        self._specs: Dict[str, ToolSpec] = {}
        self._handlers: Dict[str, Handler] = {}

    def register(self, spec: ToolSpec, handler: Handler) -> None:
        name = spec["name"]
        if name in self._specs:
            raise AtlasError("INVALID_REQUEST", f"Tool already registered: {name}")
        self._specs[name] = spec
        self._handlers[name] = handler

    def list_tools(self) -> List[ToolSpec]:
        # Deterministic ordering
        return [self._specs[k] for k in sorted(self._specs.keys())]

    def call_tool(self, name: str, arguments: JSON) -> ToolResult:
        if name not in self._handlers:
            raise AtlasError("TOOL_NOT_FOUND", f"Unknown tool: {name}")
        spec = self._specs[name]
        validate_against_schema(arguments, spec["inputSchema"])
        return self._handlers[name](arguments)


def text_result(text: str) -> ToolResult:
    return {"content": [{"type": "text", "text": text}]}


def json_result(obj: Any) -> ToolResult:
    return {"content": [{"type": "text", "text": json.dumps(obj, ensure_ascii=False)}]}
