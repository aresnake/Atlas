import bpy
import json
import sys
from pathlib import Path
from mathutils import Vector

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

def _stable3(v):
    return [round(float(v[0]), 6), round(float(v[1]), 6), round(float(v[2]), 6)]

def _bbox_world(obj):
    # bound_box is 8 points in local space
    try:
        pts = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        xs = [p.x for p in pts]; ys = [p.y for p in pts]; zs = [p.z for p in pts]
        mn = [min(xs), min(ys), min(zs)]
        mx = [max(xs), max(ys), max(zs)]
        return {"min": _stable3(mn), "max": _stable3(mx)}
    except Exception:
        return None

def _materials(obj):
    mats = []
    try:
        if hasattr(obj, "material_slots"):
            for ms in obj.material_slots:
                if ms and ms.material:
                    mats.append(ms.material.name)
    except Exception:
        pass
    return sorted(set(mats))

def _collections(obj):
    cols = []
    try:
        for c in obj.users_collection:
            cols.append(c.name)
    except Exception:
        pass
    return sorted(set(cols))

def _mesh_stats(obj):
    if obj.type != "MESH" or not obj.data:
        return None
    me = obj.data
    # NOTE: polygons/edges/verts available without depsgraph eval
    return {
        "verts": int(len(me.vertices)),
        "edges": int(len(me.edges)),
        "faces": int(len(me.polygons)),
    }

def snapshot_v2():
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
            "location": _stable3(loc),
            "rotation_euler": _stable3(rot),
            "scale": _stable3(scl),
            "hide_viewport": bool(obj.hide_viewport),
            "hide_render": bool(obj.hide_render),
            "collections": _collections(obj),
            "materials": _materials(obj),
            "bbox_world": _bbox_world(obj),
            "mesh_stats": _mesh_stats(obj),
        })

    return {
        "schema": "atlas.snapshot.v2",
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

    data = snapshot_v2()
    txt = json.dumps(data, ensure_ascii=False, sort_keys=True)

    if args["out"]:
        Path(args["out"]).parent.mkdir(parents=True, exist_ok=True)
        Path(args["out"]).write_text(txt, encoding="utf-8")
    else:
        print(txt)

if __name__ == "__main__":
    main()
