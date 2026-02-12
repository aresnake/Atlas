import bpy
import sys
import json
from pathlib import Path

def _argv_after_double_dash():
    argv = sys.argv
    if "--" in argv:
        return argv[argv.index("--")+1:]
    return []

def _parse(args):
    out = {"blend": None}
    i = 0
    while i < len(args):
        if args[i] == "--blend" and i+1 < len(args):
            out["blend"] = args[i+1]
            i += 2
            continue
        i += 1
    return out

def main():
    args = _parse(_argv_after_double_dash())
    if not args["blend"]:
        raise SystemExit("Missing --blend <path>")

    path = Path(args["blend"]).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    # factory-startup scene, just save it
    bpy.ops.wm.save_mainfile(filepath=str(path))

    print(json.dumps({"schema":"atlas.blender.init_empty.v1","blend_path":str(path)}, ensure_ascii=False, sort_keys=True))

if __name__ == "__main__":
    main()
