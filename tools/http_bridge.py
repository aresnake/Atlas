from __future__ import annotations

import json
import os
import queue
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Optional, Tuple

JSON = Dict[str, Any]


class MCPProcess:
    def __init__(self) -> None:
        self._proc: Optional[subprocess.Popen[str]] = None
        self._lock = threading.Lock()
        self._stderr_lines: "queue.Queue[str]" = queue.Queue(maxsize=500)

    def start(self) -> None:
        with self._lock:
            if self._proc and self._proc.poll() is None:
                return

            # Use current python, rely on editable install
            cmd = [os.environ.get("ATLAS_PYTHON_EXE", "python"), "-m", "atlas.mcp_stdio_server"]
            self._proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # line-buffered
            )

            assert self._proc.stderr is not None
            t = threading.Thread(target=self._drain_stderr, args=(self._proc.stderr,), daemon=True)
            t.start()

    def _drain_stderr(self, stream) -> None:
        try:
            for line in stream:
                line = (line or "").rstrip("\n")
                if not line:
                    continue
                try:
                    self._stderr_lines.put_nowait(line)
                except queue.Full:
                    # drop oldest
                    try:
                        _ = self._stderr_lines.get_nowait()
                    except queue.Empty:
                        pass
                    try:
                        self._stderr_lines.put_nowait(line)
                    except queue.Full:
                        pass
        except Exception:
            pass

    def tail_stderr(self, n: int = 50) -> list[str]:
        # non-destructive tail: snapshot queue
        items = list(self._stderr_lines.queue)
        return items[-n:]

    def request(self, method: str, params: JSON) -> JSON:
        self.start()
        assert self._proc is not None
        assert self._proc.stdin is not None
        assert self._proc.stdout is not None

        with self._lock:
            if self._proc.poll() is not None:
                # died — restart once
                self._proc = None
                self.start()
                assert self._proc is not None
                assert self._proc.stdin is not None
                assert self._proc.stdout is not None

            req = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
            self._proc.stdin.write(json.dumps(req, ensure_ascii=False) + "\n")
            self._proc.stdin.flush()

            line = self._proc.stdout.readline().strip()
            if not line:
                raise RuntimeError("MCP server returned empty stdout line")

            resp = json.loads(line)
            if "error" in resp:
                raise RuntimeError(f"MCP error: {resp['error']}")
            return resp["result"]


MCP = MCPProcess()


def _read_json(handler: BaseHTTPRequestHandler) -> JSON:
    length = int(handler.headers.get("Content-Length", "0") or "0")
    if length <= 0:
        return {}
    raw = handler.rfile.read(length).decode("utf-8")
    return json.loads(raw) if raw.strip() else {}


def _write_json(handler: BaseHTTPRequestHandler, code: int, obj: Any) -> None:
    data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        # silence default access log (n8n can be noisy)
        return

    def do_GET(self) -> None:
        try:
            if self.path == "/health":
                _write_json(self, 200, {"ok": True})
                return

            if self.path == "/tools":
                result = MCP.request("tools/list", {})
                _write_json(self, 200, {"ok": True, "result": result})
                return

            if self.path.startswith("/logs"):
                _write_json(self, 200, {"ok": True, "stderr_tail": MCP.tail_stderr(80)})
                return

            _write_json(self, 404, {"ok": False, "error": "not_found"})
        except Exception as e:
            _write_json(self, 500, {"ok": False, "error": str(e), "stderr_tail": MCP.tail_stderr(40)})

    def do_POST(self) -> None:
        try:
            if self.path == "/call":
                body = _read_json(self)
                name = body.get("name")
                arguments = body.get("arguments", {})
                if not isinstance(name, str) or not name:
                    _write_json(self, 400, {"ok": False, "error": "missing name"})
                    return
                if not isinstance(arguments, dict):
                    _write_json(self, 400, {"ok": False, "error": "arguments must be object"})
                    return

                result = MCP.request("tools/call", {"name": name, "arguments": arguments})
                _write_json(self, 200, {"ok": True, "result": result})
                return

            _write_json(self, 404, {"ok": False, "error": "not_found"})
        except Exception as e:
            _write_json(self, 500, {"ok": False, "error": str(e), "stderr_tail": MCP.tail_stderr(40)})


def main() -> int:
    host = os.environ.get("ATLAS_HTTP_HOST", "127.0.0.1")
    port = int(os.environ.get("ATLAS_HTTP_PORT", "8009"))
    httpd = HTTPServer((host, port), Handler)
    print(f"[atlas.http] listening on http://{host}:{port}", flush=True)
    httpd.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
