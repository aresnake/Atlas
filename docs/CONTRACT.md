# ATLAS Contract (v0.1)

## Doctrine
- Contract-first: tool schemas are the API.
- Deterministic: tools/list ordering and outputs must be stable.
- Headless-first: CI must pass without Blender UI.
- Data-first: avoid context-dependent ops when Blender backend is added.

## Tool Surface
- Keep <= 35 tools for Core.
- Add tools only with tests + schema + deterministic output.

## Logging
- All runs should be representable as JSONL events suitable for training loops.

## Definition of Done
- Tests green
- Tool schema stable
- Outputs deterministic
