from __future__ import annotations

from typing import Any, Dict

JSON = Dict[str, Any]


def score_from_diff_v2(d: JSON) -> float:
    # Reward shaping (v2):
    # +1 per added object
    # -2 per removed object
    # +0.2 per changed object
    # bonus: if any mesh_stats increased (more verts/faces) -> +0.3
    c = d.get("counts") or {}
    added = int(c.get("added", 0))
    removed = int(c.get("removed", 0))
    changed = int(c.get("changed", 0))
    s = float(added * 1.0 - removed * 2.0 + changed * 0.2)

    try:
        for ch in d.get("changed") or []:
            diff = ch.get("diff") or {}
            ms = diff.get("mesh_stats")
            if ms and isinstance(ms, dict):
                a = (ms.get("from") or {}) if isinstance(ms.get("from"), dict) else {}
                b = (ms.get("to") or {}) if isinstance(ms.get("to"), dict) else {}
                av = int(a.get("verts", 0)); bv = int(b.get("verts", 0))
                af = int(a.get("faces", 0)); bf = int(b.get("faces", 0))
                if bv > av or bf > af:
                    s += 0.3
                    break
    except Exception:
        pass

    return float(s)
