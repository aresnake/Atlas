from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Tuple

JSON = Dict[str, Any]


def _canon(obj: Any) -> str:
    # canonical JSON string for stable hashing/comparison
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def fingerprint(obj: Any) -> str:
    h = hashlib.sha256()
    h.update(_canon(obj).encode("utf-8"))
    return h.hexdigest()


def diff_snapshot_v1(a: JSON, b: JSON) -> JSON:
    # expects atlas.snapshot.v1
    a_objs = {o["name"]: o for o in a.get("objects", [])}
    b_objs = {o["name"]: o for o in b.get("objects", [])}

    added = sorted([n for n in b_objs.keys() if n not in a_objs])
    removed = sorted([n for n in a_objs.keys() if n not in b_objs])

    changed: List[JSON] = []
    common = sorted(set(a_objs.keys()) & set(b_objs.keys()))
    for name in common:
        oa = a_objs[name]
        ob = b_objs[name]
        # compare stable subset
        fields = ["type", "parent", "location", "rotation_euler", "scale", "hide_viewport", "hide_render"]
        diffs: Dict[str, Any] = {}
        for f in fields:
            if oa.get(f) != ob.get(f):
                diffs[f] = {"from": oa.get(f), "to": ob.get(f)}
        if diffs:
            changed.append({"name": name, "diff": diffs})

    out: JSON = {
        "schema": "atlas.snapshot.diff.v1",
        "a_fingerprint": fingerprint(a),
        "b_fingerprint": fingerprint(b),
        "added": added,
        "removed": removed,
        "changed": changed,
        "counts": {
            "added": len(added),
            "removed": len(removed),
            "changed": len(changed),
        },
    }
    return out
