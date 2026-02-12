import bpy
import sys
import json
from mathutils import Vector

def _argv_after_double_dash():
    argv = sys.argv
    if "--" in argv:
        return argv[argv.index("--")+1:]
    return []

def _parse_args(args):
    out = {"name": "ATLAS_Cube", "location": [0.0, 0.0, 0.0]}
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--name" and i+1 < len(args):
            out["name"] = args[i+1]
            i += 2
            continue
        if a == "--location" and i+3 < len(args):
            out["location"] = [float(args[i+1]), float(args[i+2]), float(args[i+3])]
            i += 4
            continue
        i += 1
    return out

def add_cube_data_first(name, location):
    scene = bpy.context.scene
    col = scene.collection

    # Create a unit cube mesh via bmesh (data-first)
    import bmesh
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=2.0)  # Blender cube default size-ish
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    obj.location = Vector(location)

    col.objects.link(obj)
    return obj

def main():
    args = _argv_after_double_dash()
    parsed = _parse_args(args)
    obj = add_cube_data_first(parsed["name"], parsed["location"])

    result = {
        "schema": "atlas.blender.add_cube.v1",
        "created": {"name": obj.name, "type": obj.type},
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))

if __name__ == "__main__":
    main()
