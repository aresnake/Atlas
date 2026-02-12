import json
import subprocess
import sys

def test_mcp_stdio_tools_list_and_ping():
    p = subprocess.Popen(
        [sys.executable, "-m", "atlas.mcp_stdio_server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        p.stdin.write(json.dumps({"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}) + "\n")
        p.stdin.flush()
        line = p.stdout.readline().strip()
        resp = json.loads(line)
        assert resp["id"] == 1
        assert "tools" in resp["result"]

        p.stdin.write(json.dumps({"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"atlas.ping","arguments":{}}}) + "\n")
        p.stdin.flush()
        line2 = p.stdout.readline().strip()
        resp2 = json.loads(line2)
        assert resp2["id"] == 2
        assert resp2["result"]["content"][0]["text"] == "pong"
    finally:
        p.terminate()
