import bpy
import json
import sys
from mathutils import Vector

def _argv_after_double_dash():
    argv = sys.argv
    if "--" in argv:
        return argv[argv.index("--")+1:]
    return []

def _stable_vec(v):
    # stable rounding (avoid float noise)
    return [round(float(v[0]), 6), round(float(v[1]), 6), round(float(v[2]), 6)]

def snapshot_v1():
    scene = bpy.context.scene

    objs = []
    # deterministic order by name
    for obj in sorted(scene.objects, key=lambda o: o.name):
        # only object basics for v1
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

    data = {
        "schema": "atlas.snapshot.v1",
        "blender": {
            "version_string": bpy.app.version_string,
            "version": list(bpy.app.version),
        },
        "scene": {
            "name": scene.name,
            "frame_current": int(scene.frame_current),
            "unit_system": getattr(scene.unit_settings, "system", None),
        },
        "objects": objs,
    }
    return data

def main():
    args = _argv_after_double_dash()
    out_path = None
    for i, a in enumerate(args):
        if a == "--out" and i+1 < len(args):
            out_path = args[i+1]
    data = snapshot_v1()
    txt = json.dumps(data, ensure_ascii=False, sort_keys=True)

    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(txt)
    else:
        print(txt)

if __name__ == "__main__":
    main()
