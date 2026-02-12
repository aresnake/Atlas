from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

from .contract import AtlasError

JSON = Dict[str, Any]


def get_blender_exe() -> str:
    exe = os.environ.get("ATLAS_BLENDER_EXE")
    if not exe:
        raise AtlasError(
            "INVALID_REQUEST",
            "ATLAS_BLENDER_EXE is not set. Provide path to blender.exe in env.",
        )
    return exe


def _parse_json_from_stdout(stdout: str) -> JSON:
    s = (stdout or "").strip()
    if not s:
        raise AtlasError("INTERNAL_ERROR", "Blender produced empty stdout")

    # 1) Fast path: whole stdout is JSON
    try:
        return json.loads(s)
    except Exception:
        pass

    # 2) Try line-by-line from the end (common case: last line is JSON)
    lines = [ln.strip() for ln in s.splitlines() if ln.strip()]
    for ln in reversed(lines):
        if not (ln.startswith("{") and ln.endswith("}")):
            continue
        try:
            return json.loads(ln)
        except Exception:
            continue

    # 3) Try to extract a JSON object by slicing from last '{' to last '}'
    last_lbrace = s.rfind("{")
    last_rbrace = s.rfind("}")
    if 0 <= last_lbrace < last_rbrace:
        candidate = s[last_lbrace : last_rbrace + 1]
        try:
            return json.loads(candidate)
        except Exception:
            pass

    raise AtlasError(
        "INTERNAL_ERROR",
        "Could not parse JSON from Blender stdout",
        data={"stdout_tail": s[-4000:]},
    )


def run_blender_script(
    script_path: Path,
    *,
    out_json_path: Optional[Path] = None,
    extra_args: Optional[Sequence[str]] = None,
) -> JSON:
    exe = get_blender_exe()
    script_path = script_path.resolve()
    extra_args = list(extra_args or [])

    cmd = [exe, "-b", "--factory-startup", "--python", str(script_path), "--"]

    if out_json_path:
        out_json_path = out_json_path.resolve()
        out_json_path.parent.mkdir(parents=True, exist_ok=True)
        cmd += ["--out", str(out_json_path)]

    cmd += list(extra_args)

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as e:
        raise AtlasError("INTERNAL_ERROR", f"Failed to start Blender: {e}")

    if proc.returncode != 0:
        raise AtlasError(
            "INTERNAL_ERROR",
            "Blender returned non-zero exit code",
            data={
                "returncode": proc.returncode,
                "stdout": (proc.stdout or "")[-4000:],
                "stderr": (proc.stderr or "")[-4000:],
            },
        )

    if out_json_path:
        txt = out_json_path.read_text(encoding="utf-8")
        return json.loads(txt)

    return _parse_json_from_stdout(proc.stdout)
