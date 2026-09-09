from __future__ import annotations

import json
import sqlite3
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class DecisionStore:
    """SQLite-backed decision log.

    Some deployment targets for this API (e.g. a Python serverless
    function runtime) expose a read-only filesystem outside of a temp
    directory. If the configured on-disk path can't be created/opened for
    writing, fall back to a process-local in-memory database instead of
    crashing the whole application at import time -- decision persistence
    is a convenience feature, not something worth taking the API down for.
    """

    def __init__(self, path: Path):
        self.path = Path(path)
        self._memory_conn = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._init()
        except (OSError, sqlite3.Error) as exc:
            print(
                f"WARNING: DecisionStore could not open {self.path!s} ({exc!r}); "
                "falling back to an in-memory store. Decisions will not persist "
                "across restarts.",
                file=sys.stderr,
            )
            traceback.print_exc()
            self._memory_conn = sqlite3.connect(":memory:", check_same_thread=False)
            self._memory_conn.row_factory = sqlite3.Row
            self._init()

    def _connect(self):
        if self._memory_conn is not None:
            return self._memory_conn
        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row
        return con

    def _init(self):
        with self._connect() as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    request_json TEXT NOT NULL,
                    response_json TEXT NOT NULL,
                    risk REAL NOT NULL,
                    severity TEXT NOT NULL,
                    action TEXT NOT NULL
                )
            """)
            con.execute("CREATE INDEX IF NOT EXISTS idx_decisions_created ON decisions(created_at DESC)")

    def record(self, request: dict[str, Any], response: dict[str, Any]) -> int:
        created = datetime.now(timezone.utc).isoformat()
        with self._connect() as con:
            cur = con.execute(
                "INSERT INTO decisions(created_at, request_json, response_json, risk, severity, action) VALUES(?,?,?,?,?,?)",
                (created, json.dumps(request), json.dumps(response), float(response["risk"]), response["severity"], response["action"]),
            )
            return int(cur.lastrowid)

    def recent(self, limit: int = 20) -> list[dict]:
        with self._connect() as con:
            rows = con.execute(
                "SELECT id, created_at, risk, severity, action, request_json, response_json FROM decisions ORDER BY id DESC LIMIT ?",
                (int(limit),),
            ).fetchall()
        return [{
            "id": r["id"], "created_at": r["created_at"], "risk": r["risk"], "severity": r["severity"], "action": r["action"],
            "request": json.loads(r["request_json"]), "response": json.loads(r["response_json"]),
        } for r in rows]

    def summary(self) -> dict:
        with self._connect() as con:
            row = con.execute("SELECT COUNT(*) n, AVG(risk) avg_risk, MAX(risk) max_risk FROM decisions").fetchone()
            severities = con.execute("SELECT severity, COUNT(*) n FROM decisions GROUP BY severity").fetchall()
        return {
            "decision_count": int(row["n"]),
            "average_risk": float(row["avg_risk"] or 0.0),
            "maximum_risk": float(row["max_risk"] or 0.0),
            "severity_counts": {r["severity"]: int(r["n"]) for r in severities},
        }
