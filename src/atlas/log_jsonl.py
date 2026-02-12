from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

JSON = Dict[str, Any]


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class LogEvent:
    ts: str
    kind: str
    payload: JSON
    run_id: str
    step: int
    ok: bool
    error: Optional[JSON] = None

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


class JsonlLogger:
    def __init__(self, path: Path, run_id: str):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.run_id = run_id
        self.step = 0

    def write(self, kind: str, payload: JSON, ok: bool = True, error: Optional[JSON] = None) -> None:
        ev = LogEvent(
            ts=_utc_iso(),
            kind=kind,
            payload=payload,
            run_id=self.run_id,
            step=self.step,
            ok=ok,
            error=error,
        )
        self.step += 1
        with self.path.open("a", encoding="utf-8") as f:
            f.write(ev.to_json() + "\n")
