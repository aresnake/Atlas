from atlas.tools_core import build_registry


def test_list_tools_is_deterministic_and_contains_ping():
    reg = build_registry()
    tools = reg.list_tools()
    names = [t["name"] for t in tools]
    assert names == sorted(names)
    assert "atlas.ping" in names


def test_ping_returns_pong():
    reg = build_registry()
    res = reg.call_tool("atlas.ping", {})
    assert res["content"][0]["text"] == "pong"


def test_echo_validates_schema():
    reg = build_registry()
    res = reg.call_tool("atlas.echo", {"text": "hello"})
    assert "hello" in res["content"][0]["text"]
