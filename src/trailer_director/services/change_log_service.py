from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ChangeLogService:
    """Append-only JSON change log for recovery decisions."""

    def __init__(self, path: str | Path = "sample_run/decision_log.json") -> None:
        self.path = Path(path)

    def append(self, event: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)

        entries: list[dict[str, Any]] = []
        if self.path.exists():
            entries = json.loads(self.path.read_text(encoding="utf-8"))

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **event,
        }
        entries.append(record)
        self.path.write_text(
            json.dumps(entries, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def read(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        return json.loads(self.path.read_text(encoding="utf-8"))
