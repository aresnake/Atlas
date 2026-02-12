import os
import json
import pytest

from atlas.tools_core import build_registry


def test_benchmark_smoke_schema_only(tmp_path):
    # This test is schema/shape only. Runtime execution needs Blender env.
    reg = build_registry()
    assert any(t["name"] == "atlas.benchmark.smoke_v1" for t in reg.list_tools())


def test_benchmark_smoke_runtime(tmp_path):
    if not os.environ.get("ATLAS_BLENDER_EXE"):
        pytest.skip("ATLAS_BLENDER_EXE not set")

    reg = build_registry()
    res = reg.call_tool("atlas.benchmark.smoke_v1", {"out_dir": str(tmp_path / "bench")})
    data = json.loads(res["content"][0]["text"])
    assert data["schema"] == "atlas.benchmark.smoke.v1"
    assert data["total_score"] >= 0.0
    assert len(data["steps"]) == 3
