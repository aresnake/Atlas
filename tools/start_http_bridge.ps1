param(
  [string]$Port = "8009",
  [string]$BlenderExe = "",
  [string]$PythonExe = ""
)

if (-not $PythonExe) { $PythonExe = (Get-Command python).Source }

if (-not $BlenderExe) {
  if ($env:ATLAS_BLENDER_EXE) { $BlenderExe = $env:ATLAS_BLENDER_EXE }
  else { $BlenderExe = "C:\Program Files\Blender Foundation\Blender 5.0\blender.exe" }
}

$env:ATLAS_BLENDER_EXE = $BlenderExe
$env:ATLAS_HTTP_PORT = $Port
$env:ATLAS_PYTHON_EXE = $PythonExe

& $PythonExe .\tools\http_bridge.py
