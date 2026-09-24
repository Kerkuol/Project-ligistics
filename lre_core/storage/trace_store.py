"""
Хранилище трассировок логического вывода и обратной связи.
Реализовано с использованием SQLite и оперативной памяти для быстродействия.
"""
import sqlite3
import json
from typing import Optional, List, Dict, Any
from pathlib import Path

from ..schemas.response import GraphTrace, FeedbackPayload
from ..config import settings

class TraceStore:
    def __init__(self, db_path: Path = settings.DB_PATH):
        self.db_path = db_path
        self._memory_cache: Dict[str, GraphTrace] = {}
        self._latest_trace_id: Optional[str] = None
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS traces (
                    trace_id TEXT PRIMARY KEY,
                    request_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    trace_json TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS feedbacks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trace_id TEXT NOT NULL,
                    request_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    feedback_json TEXT NOT NULL
                )
            """)
            conn.commit()

    def save_trace(self, trace: GraphTrace):
        self._memory_cache[trace.trace_id] = trace
        self._latest_trace_id = trace.trace_id
        
        # Ротация кэша памяти
        if len(self._memory_cache) > settings.MAX_TRACES_HISTORY:
            oldest_key = next(iter(self._memory_cache))
            del self._memory_cache[oldest_key]

        trace_json = trace.model_dump_json()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO traces (trace_id, request_id, trace_json) VALUES (?, ?, ?)",
                (trace.trace_id, trace.request_id, trace_json)
            )
            conn.commit()

    def get_trace(self, trace_id: str) -> Optional[GraphTrace]:
        if trace_id in self._memory_cache:
            return self._memory_cache[trace_id]

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT trace_json FROM traces WHERE trace_id = ?", (trace_id,))
            row = cursor.fetchone()
            if row:
                data = json.loads(row[0])
                trace = GraphTrace(**data)
                self._memory_cache[trace_id] = trace
                return trace
        return None

    def get_latest_trace(self) -> Optional[GraphTrace]:
        if self._latest_trace_id and self._latest_trace_id in self._memory_cache:
            return self._memory_cache[self._latest_trace_id]

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT trace_json FROM traces ORDER BY created_at DESC LIMIT 1")
            row = cursor.fetchone()
            if row:
                data = json.loads(row[0])
                trace = GraphTrace(**data)
                self._latest_trace_id = trace.trace_id
                return trace
        return None

    def list_traces(self, limit: int = 20) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT trace_id, request_id, created_at FROM traces ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            return [
                {"trace_id": row[0], "request_id": row[1], "created_at": row[2]}
                for row in cursor.fetchall()
            ]

    def save_feedback(self, feedback: FeedbackPayload):
        feedback_json = feedback.model_dump_json()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO feedbacks (trace_id, request_id, feedback_json) VALUES (?, ?, ?)",
                (feedback.trace_id, feedback.request_id, feedback_json)
            )
            conn.commit()

trace_store = TraceStore()
