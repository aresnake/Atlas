from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

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


def run_blender_script(script_path: Path, *, out_json_path: Optional[Path] = None) -> JSON:
    exe = get_blender_exe()
    script_path = script_path.resolve()

    cmd = [exe, "-b", "--factory-startup", "--python", str(script_path)]
    if out_json_path:
        out_json_path = out_json_path.resolve()
        out_json_path.parent.mkdir(parents=True, exist_ok=True)
        cmd += ["--", "--out", str(out_json_path)]

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
            data={"returncode": proc.returncode, "stdout": proc.stdout[-4000:], "stderr": proc.stderr[-4000:]},
        )

    if out_json_path:
        txt = out_json_path.read_text(encoding="utf-8")
        return json.loads(txt)

    # fallback: stdout contains JSON
    txt = proc.stdout.strip()
    if not txt:
        raise AtlasError("INTERNAL_ERROR", "Blender produced empty stdout", data={"stderr": proc.stderr[-4000:]})
    return json.loads(txt)
