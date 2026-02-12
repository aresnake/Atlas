param(
  [string] = "out/bench_smoke",
  [string] = ""
)

if (-not ) {
  Write-Error "ATLAS_BLENDER_EXE is not set. Example: $env:ATLAS_BLENDER_EXE='C:\Program Files\Blender Foundation\Blender 5.0\blender.exe'"
  exit 1
}

python - << 'PY'
import json, os
from atlas.tools_core import build_registry

reg = build_registry()
args = {"out_dir": os.environ.get("ATLAS_OUT_DIR", None) or r"%OutDir%"}
rid = r"%RunId%"
if rid:
    args["run_id"] = rid

res = reg.call_tool("atlas.benchmark.smoke_v1", args)
print(res["content"][0]["text"])
PY
