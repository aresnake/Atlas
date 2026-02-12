from atlas.snapshot_diff import diff_snapshot_v1


def _snap(objs):
    return {"schema": "atlas.snapshot.v1", "objects": objs}


def test_diff_added_removed_changed():
    a = _snap([{"name": "Cube", "type": "MESH", "parent": None, "location": [0,0,0], "rotation_euler":[0,0,0], "scale":[1,1,1], "hide_viewport": False, "hide_render": False}])
    b = _snap([
        {"name": "Cube", "type": "MESH", "parent": None, "location": [1,0,0], "rotation_euler":[0,0,0], "scale":[1,1,1], "hide_viewport": False, "hide_render": False},
        {"name": "Light", "type": "LIGHT", "parent": None, "location": [0,0,0], "rotation_euler":[0,0,0], "scale":[1,1,1], "hide_viewport": False, "hide_render": False},
    ])

    d = diff_snapshot_v1(a, b)
    assert d["schema"] == "atlas.snapshot.diff.v1"
    assert d["counts"]["added"] == 1
    assert d["added"] == ["Light"]
    assert d["counts"]["removed"] == 0
    assert d["counts"]["changed"] == 1
    assert d["changed"][0]["name"] == "Cube"
    assert "location" in d["changed"][0]["diff"]
