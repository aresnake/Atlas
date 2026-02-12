import json
import os
from pathlib import Path

import pytest

from atlas.tools_core import build_registry


def test_run_step_v1_smoke(tmp_path):
    if not os.environ.get("ATLAS_BLENDER_EXE"):
        pytest.skip("ATLAS_BLENDER_EXE not set")

    reg = build_registry()

    out_dir = tmp_path / "snaps"
    res = reg.call_tool(
        "atlas.run.step_v1",
        {
            "action_tool": "atlas.echo",
            "action_args": {"text": "hello"},
            "snapshot_out_dir": str(out_dir),
        },
    )

    data = json.loads(res["content"][0]["text"])
    assert data["schema"] == "atlas.run.step.v1"
    assert "run_id" in data
    assert Path(data["paths"]["log"]).exists()
    assert Path(data["paths"]["before"]).exists()
    assert Path(data["paths"]["after"]).exists()
    assert "diff" in data
    assert "score" in data
