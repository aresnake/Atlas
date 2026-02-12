from __future__ import annotations

import json
import sys
import traceback
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .contract import AtlasError
from .tools_core import build_registry

JSON = Dict[str, Any]


# MCP-ish error codes (numeric) — keep stable
ERR_INVALID_REQUEST = -32600
ERR_METHOD_NOT_FOUND = -32601
ERR_INVALID_PARAMS = -32602
ERR_INTERNAL_ERROR = -32603


def _eprint(*args: Any) -> None:
    print(*args, file=sys.stderr, flush=True)


def _readline() -> Optional[str]:
    line = sys.stdin.readline()
    if not line:
        return None
    return line.strip()


def _write(obj: JSON) -> None:
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _is_obj(x: Any) -> bool:
    return isinstance(x, dict)


def _as_error(code: int, message: str, data: Optional[JSON] = None) -> JSON:
    err: JSON = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return err


def _handle_tools_list(req: JSON) -> JSON:
    reg = build_registry()
    tools = reg.list_tools()
    return {"tools": tools}


def _handle_tools_call(req: JSON) -> JSON:
    params = req.get("params") or {}
    if not _is_obj(params):
        raise AtlasError("INVALID_ARGUMENTS", "params must be an object")

    name = params.get("name")
    arguments = params.get("arguments")

    if not isinstance(name, str) or not name:
        raise AtlasError("INVALID_ARGUMENTS", "params.name must be a non-empty string")
    if arguments is None:
        arguments = {}
    if not _is_obj(arguments):
        raise AtlasError("INVALID_ARGUMENTS", "params.arguments must be an object")

    reg = build_registry()
    return reg.call_tool(name, arguments)


def _dispatch(method: str, req: JSON) -> JSON:
    if method == "tools/list":
        return _handle_tools_list(req)
    if method == "tools/call":
        return _handle_tools_call(req)
    raise KeyError(method)


def serve_stdio() -> int:
    _eprint("[atlas.mcp] boot")

    while True:
        line = _readline()
        if line is None:
            _eprint("[atlas.mcp] eof")
            return 0
        if not line:
            continue

        try:
            req = json.loads(line)
        except Exception:
            # not JSON -> ignore (or you can hard error)
            _eprint("[atlas.mcp] invalid json line ignored")
            continue

        if not _is_obj(req) or req.get("jsonrpc") != "2.0" or "method" not in req:
            # invalid request
            rid = req.get("id") if _is_obj(req) else None
            if rid is not None:
                _write({"jsonrpc": "2.0", "id": rid, "error": _as_error(ERR_INVALID_REQUEST, "Invalid Request")})
            continue

        method = req.get("method")
        rid = req.get("id")  # may be absent for notifications

        # notifications: no response
        is_notification = "id" not in req

        try:
            result = _dispatch(method, req)
            if not is_notification:
                _write({"jsonrpc": "2.0", "id": rid, "result": result})
        except KeyError:
            if not is_notification:
                _write({"jsonrpc": "2.0", "id": rid, "error": _as_error(ERR_METHOD_NOT_FOUND, f"Method not found: {method}")})
        except AtlasError as e:
            # Map to INVALID_PARAMS unless it's internal
            code = ERR_INVALID_PARAMS if e.code != "INTERNAL_ERROR" else ERR_INTERNAL_ERROR
            if not is_notification:
                _write({"jsonrpc": "2.0", "id": rid, "error": _as_error(code, e.message, e.data)})
        except Exception as e:
            tb = traceback.format_exc(limit=8)
            _eprint("[atlas.mcp] internal error:", tb)
            if not is_notification:
                _write({"jsonrpc": "2.0", "id": rid, "error": _as_error(ERR_INTERNAL_ERROR, "Internal error", {"traceback": tb})})


if __name__ == "__main__":
    raise SystemExit(serve_stdio())
