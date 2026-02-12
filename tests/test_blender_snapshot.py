import json
import os
from pathlib import Path

import pytest

from atlas.tools_core import build_registry


@pytest.mark.skipif(
    not (Path(__file__).resolve().parents[1] / "tools" / "blender_snapshot_v1.py").exists(),
    reason="blender script missing",
)
def test_blender_snapshot_v1(tmp_path):
    # If Blender path isn't provided, skip (CI can set it explicitly)
    blender_exe = os.environ.get("ATLAS_BLENDER_EXE")
    if not blender_exe:
        pytest.skip("ATLAS_BLENDER_EXE not set")

    reg = build_registry()
    out_path = tmp_path / "snapshot.json"
    res = reg.call_tool("atlas.blender.snapshot_v1", {"out_path": str(out_path)})

    txt = res["content"][0]["text"]
    data = json.loads(txt)

    assert data["schema"] == "atlas.snapshot.v1"
    assert "blender" in data
    assert "scene" in data
    assert "objects" in data
    assert isinstance(data["objects"], list)
