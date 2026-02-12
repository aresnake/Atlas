import json
import os
import subprocess
import sys

def send(p, obj):
    p.stdin.write(json.dumps(obj, ensure_ascii=False) + "\n")
    p.stdin.flush()
    line = p.stdout.readline().strip()
    if not line:
        raise RuntimeError("No response from server (stdout empty).")
    return json.loads(line)

if __name__ == "__main__":
    # Start server via python -m atlas.mcp_stdio_server style
    p = subprocess.Popen(
        [sys.executable, "-m", "atlas.mcp_stdio_server"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        r1 = send(p, {"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}})
        print("tools/list ok:", "tools" in r1.get("result", {}))

        # Call ping
        r2 = send(p, {"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"atlas.ping","arguments":{}}})
        print("tools/call ping:", r2["result"]["content"][0]["text"])

        # Optional: Blender benchmark if env set
        if os.environ.get("ATLAS_BLENDER_EXE"):
            r3 = send(
                p,
                {"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"atlas.benchmark.smoke_v1","arguments":{"out_dir":"out/bench_smoke"}}},
            )
            txt = r3["result"]["content"][0]["text"]
            print("bench:", txt[:120] + "...")
        else:
            print("bench: skipped (ATLAS_BLENDER_EXE not set)")
    finally:
        p.terminate()
