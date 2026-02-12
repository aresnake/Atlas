from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from .contract import AtlasError, ToolResult
from .log_jsonl import JsonlLogger
from .registry import ToolRegistry
from .snapshot_diff import diff_snapshot_v1

JSON = Dict[str, Any]


def _default_run_id() -> str:
    return uuid.uuid4().hex[:12]


def _score_from_diff(d: JSON) -> float:
    c = d.get("counts") or {}
    added = int(c.get("added", 0))
    removed = int(c.get("removed", 0))
    changed = int(c.get("changed", 0))
    return float(added * 1.0 + changed * 0.2 - removed * 2.0)


def _extract_json_text(res: ToolResult) -> JSON:
    try:
        txt = res["content"][0]["text"]
    except Exception as e:
        raise AtlasError("INTERNAL_ERROR", f"Invalid ToolResult content: {e}")
    import json
    return json.loads(txt)


def run_step_v1(
    reg: ToolRegistry,
    *,
    action_tool: str,
    action_args: JSON,
    snapshot_out_dir: Path,
    run_id: Optional[str] = None,
    workspace_blend_path: Optional[Path] = None,
) -> JSON:
    run_id = run_id or _default_run_id()
    snapshot_out_dir.mkdir(parents=True, exist_ok=True)

    # workspace blend
    if workspace_blend_path is None:
        workspace_blend_path = snapshot_out_dir / f"{run_id}.workspace.blend"
    workspace_blend_path = workspace_blend_path.resolve()

    if not workspace_blend_path.exists():
        reg.call_tool("atlas.blender.init_empty_v1", {"blend_path": str(workspace_blend_path)})

    log_path = Path("out") / "runs" / f"{run_id}.jsonl"
    logger = JsonlLogger(log_path, run_id)

    # 1) snapshot_before (from workspace)
    before_path = snapshot_out_dir / f"{run_id}.before.json"
    snap_before = reg.call_tool(
        "atlas.blender.snapshot_v1",
        {"out_path": str(before_path), "blend_path": str(workspace_blend_path)},
    )
    before = _extract_json_text(snap_before)
    logger.write("snapshot_before", {"path": str(before_path), "blend_path": str(workspace_blend_path), "snapshot": before})

    # 2) action (if blender tool, inject blend_path automatically if not set)
    aargs = dict(action_args or {})
    if action_tool.startswith("atlas.blender.") and "blend_path" not in aargs:
        aargs["blend_path"] = str(workspace_blend_path)

    try:
        action_res = reg.call_tool(action_tool, aargs)
        action_ok = True
        action_err = None
        action_payload = {"tool": action_tool, "args": aargs, "result": action_res}
    except AtlasError as e:
        action_ok = False
        action_err = {"code": e.code, "message": e.message, "data": e.data}
        action_payload = {"tool": action_tool, "args": aargs}

    logger.write("action", action_payload, ok=action_ok, error=action_err)

    # 3) snapshot_after (from same workspace)
    after_path = snapshot_out_dir / f"{run_id}.after.json"
    snap_after = reg.call_tool(
        "atlas.blender.snapshot_v1",
        {"out_path": str(after_path), "blend_path": str(workspace_blend_path)},
    )
    after = _extract_json_text(snap_after)
    logger.write("snapshot_after", {"path": str(after_path), "blend_path": str(workspace_blend_path), "snapshot": after})

    # 4) diff
    d = diff_snapshot_v1(before, after)
    logger.write("diff", d)

    # 5) score
    score = _score_from_diff(d)
    logger.write("score", {"score": score})

    return {
        "schema": "atlas.run.step.v1",
        "run_id": run_id,
        "action": {"tool": action_tool, "args": aargs, "ok": action_ok, "error": action_err},
        "paths": {
            "log": str(log_path),
            "before": str(before_path),
            "after": str(after_path),
            "workspace_blend": str(workspace_blend_path),
        },
        "diff": d,
        "score": score,
    }
