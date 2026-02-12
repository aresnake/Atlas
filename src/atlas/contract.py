from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, TypedDict


JSON = Dict[str, Any]


class ToolSpec(TypedDict):
    name: str
    description: str
    inputSchema: JSON


class ToolResult(TypedDict):
    # MCP-style "content" (text only for v0.1)
    content: List[Dict[str, str]]


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: JSON


ErrorCode = Literal[
    "INVALID_REQUEST",
    "TOOL_NOT_FOUND",
    "INVALID_ARGUMENTS",
    "INTERNAL_ERROR",
]


class AtlasError(Exception):
    def __init__(self, code: ErrorCode, message: str, data: Optional[JSON] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data or {}
