import bpy
import json
import sys
from pathlib import Path

def _argv_after_double_dash():
    argv = sys.argv
    if "--" in argv:
        return argv[argv.index("--")+1:]
    return []

def _parse(args):
    out = {"out": None, "blend": None}
    i = 0
    while i < len(args):
        if args[i] == "--out" and i+1 < len(args):
            out["out"] = args[i+1]
            i += 2
            continue
        if args[i] == "--blend" and i+1 < len(args):
            out["blend"] = args[i+1]
            i += 2
            continue
        i += 1
    return out

def _stable_vec(v):
    return [round(float(v[0]), 6), round(float(v[1]), 6), round(float(v[2]), 6)]

def snapshot_v1():
    scene = bpy.context.scene
    objs = []
    for obj in sorted(scene.objects, key=lambda o: o.name):
        loc = obj.matrix_world.to_translation()
        rot = obj.matrix_world.to_euler("XYZ")
        scl = obj.matrix_world.to_scale()
        objs.append({
            "name": obj.name,
            "type": obj.type,
            "parent": obj.parent.name if obj.parent else None,
            "location": _stable_vec(loc),
            "rotation_euler": _stable_vec(rot),
            "scale": _stable_vec(scl),
            "hide_viewport": bool(obj.hide_viewport),
            "hide_render": bool(obj.hide_render),
        })
    return {
        "schema": "atlas.snapshot.v1",
        "blender": {"version_string": bpy.app.version_string, "version": list(bpy.app.version)},
        "scene": {"name": scene.name, "frame_current": int(scene.frame_current)},
        "objects": objs,
    }

def main():
    args = _parse(_argv_after_double_dash())

    if args["blend"]:
        p = Path(args["blend"]).resolve()
        if p.exists():
            bpy.ops.wm.open_mainfile(filepath=str(p))

    data = snapshot_v1()
    txt = json.dumps(data, ensure_ascii=False, sort_keys=True)

    if args["out"]:
        with open(args["out"], "w", encoding="utf-8") as f:
            f.write(txt)
    else:
        print(txt)

if __name__ == "__main__":
    main()
