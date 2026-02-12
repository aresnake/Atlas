import json
import os
from pathlib import Path

import pytest

from atlas.tools_core import build_registry


def test_blender_add_cube_v1_changes_scene(tmp_path):
    if not os.environ.get("ATLAS_BLENDER_EXE"):
        pytest.skip("ATLAS_BLENDER_EXE not set")

    reg = build_registry()

    # run step with real blender action
    out_dir = tmp_path / "snaps"
    res = reg.call_tool(
        "atlas.run.step_v1",
        {
            "action_tool": "atlas.blender.add_cube_v1",
            "action_args": {"name": "ATLAS_Cube_01", "location": {"x": 1.0, "y": 2.0, "z": 3.0}},
            "snapshot_out_dir": str(out_dir),
        },
    )

    data = json.loads(res["content"][0]["text"])
    d = data["diff"]
    assert d["counts"]["added"] >= 1
    assert any("ATLAS_Cube_01" in n for n in d["added"])
    assert data["score"] > 0
