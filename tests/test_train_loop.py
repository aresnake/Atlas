import os
import json
import pytest

from atlas.tools_core import build_registry


def test_train_loop_tool_is_registered():
    reg = build_registry()
    assert any(t["name"] == "atlas.train.loop_v1" for t in reg.list_tools())


def test_snapshot_v2_tool_is_registered():
    reg = build_registry()
    assert any(t["name"] == "atlas.blender.snapshot_v2" for t in reg.list_tools())


def test_train_loop_runtime(tmp_path):
    if not os.environ.get("ATLAS_BLENDER_EXE"):
        pytest.skip("ATLAS_BLENDER_EXE not set")

    reg = build_registry()
    res = reg.call_tool("atlas.train.loop_v1", {"steps": 3, "out_dir": str(tmp_path / "train3"), "seed": 123})
    data = json.loads(res["content"][0]["text"])
    assert data["schema"] == "atlas.train.loop.v1"
    assert data["steps"] == 3
    assert len(data["history"]) == 3
