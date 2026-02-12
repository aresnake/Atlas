from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List

JSON = Dict[str, Any]


def canon(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def fingerprint(obj: Any) -> str:
    h = hashlib.sha256()
    h.update(canon(obj).encode("utf-8"))
    return h.hexdigest()


def obj_fingerprint_v2(o: JSON) -> str:
    # Stable subset (avoid volatile fields if any appear later)
    stable = {
        "name": o.get("name"),
        "type": o.get("type"),
        "parent": o.get("parent"),
        "location": o.get("location"),
        "rotation_euler": o.get("rotation_euler"),
        "scale": o.get("scale"),
        "hide_viewport": o.get("hide_viewport"),
        "hide_render": o.get("hide_render"),
        "collections": o.get("collections") or [],
        "materials": o.get("materials") or [],
        "bbox_world": o.get("bbox_world"),
        "mesh_stats": o.get("mesh_stats"),
    }
    return fingerprint(stable)


def _index_by_name(snap: JSON) -> Dict[str, JSON]:
    return {o.get("name"): o for o in (snap.get("objects") or []) if isinstance(o, dict) and o.get("name")}


def diff_snapshot_v2(a: JSON, b: JSON) -> JSON:
    a_objs = _index_by_name(a)
    b_objs = _index_by_name(b)

    added = sorted([n for n in b_objs.keys() if n not in a_objs])
    removed = sorted([n for n in a_objs.keys() if n not in b_objs])

    changed: List[JSON] = []
    common = sorted(set(a_objs.keys()) & set(b_objs.keys()))

    fields = [
        "type","parent",
        "location","rotation_euler","scale",
        "hide_viewport","hide_render",
        "collections","materials",
        "bbox_world","mesh_stats",
    ]

    for name in common:
        oa = a_objs[name]
        ob = b_objs[name]
        diffs: Dict[str, Any] = {}
        for f in fields:
            if oa.get(f) != ob.get(f):
                diffs[f] = {"from": oa.get(f), "to": ob.get(f)}
        if diffs:
            changed.append({
                "name": name,
                "a_fp": obj_fingerprint_v2(oa),
                "b_fp": obj_fingerprint_v2(ob),
                "diff": diffs,
            })

    out: JSON = {
        "schema": "atlas.snapshot.diff.v2",
        "a_fingerprint": fingerprint(a),
        "b_fingerprint": fingerprint(b),
        "added": added,
        "removed": removed,
        "changed": changed,
        "counts": {"added": len(added), "removed": len(removed), "changed": len(changed)},
    }
    return out
