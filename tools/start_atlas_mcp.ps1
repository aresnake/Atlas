param(
  [string]$BlenderExe = "",
  [string]$PythonExe = ""
)

if (-not $PythonExe) {
  $PythonExe = (Get-Command python).Source
}

if (-not $BlenderExe) {
  if ($env:ATLAS_BLENDER_EXE) { $BlenderExe = $env:ATLAS_BLENDER_EXE }
  else { $BlenderExe = "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe" }
}

$env:ATLAS_BLENDER_EXE = $BlenderExe

# IMPORTANT: stderr only logs, stdout jsonrpc
& $PythonExe -m atlas.mcp_stdio_server
