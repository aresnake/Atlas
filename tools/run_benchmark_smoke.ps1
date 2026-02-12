param(
  [string]$OutDir = "out/bench_smoke",
  [string]$RunId = ""
)

if (-not $env:ATLAS_BLENDER_EXE) {
  Write-Error "ATLAS_BLENDER_EXE is not set. Example: `$env:ATLAS_BLENDER_EXE='C:\Program Files\Blender Foundation\Blender 5.0\blender.exe'"
  exit 1
}

$env:ATLAS_BENCH_OUT_DIR = $OutDir
$env:ATLAS_BENCH_RUN_ID  = $RunId

python -c "import os, json; from atlas.tools_core import build_registry; reg=build_registry(); args={'out_dir': os.environ['ATLAS_BENCH_OUT_DIR']}; rid=os.environ.get('ATLAS_BENCH_RUN_ID') or ''; 
if rid.strip(): args['run_id']=rid.strip(); 
res=reg.call_tool('atlas.benchmark.smoke_v1', args); print(res['content'][0]['text'])"
