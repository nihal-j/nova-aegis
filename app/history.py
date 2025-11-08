"""History and audit log system for Aegis."""
import sqlite3
import json
import time
from pathlib import Path
from typing import List, Dict, Optional

# Find project root (where app/ directory is located)
_PROJECT_ROOT = Path(__file__).parent.parent
# Use project root for database (consistent location)
DB_PATH = _PROJECT_ROOT / "aegis_history.db"


def init_db():
    """Initialize the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS risk_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT UNIQUE,
            timestamp REAL,
            status TEXT,
            risk_score INTEGER,
            checks TEXT,
            explanation TEXT,
            diff TEXT,
            stdout TEXT,
            action TEXT,
            approved BOOLEAN DEFAULT 0,
            approved_by TEXT,
            approved_at REAL,
            execution_time REAL,
            created_at REAL DEFAULT (julianday('now'))
        )
    """)
    conn.commit()
    conn.close()


def save_risk_card(risk_card: dict, request_id: str = None, execution_time: float = None) -> str:
    """Save a risk card to history. Returns request_id."""
    if request_id is None:
        request_id = f"req_{int(time.time() * 1000)}"
    
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT OR REPLACE INTO risk_cards 
        (request_id, timestamp, status, risk_score, checks, explanation, diff, stdout, action, execution_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        request_id,
        risk_card.get("ts", time.time()),
        risk_card.get("status", "unknown"),
        risk_card.get("risk_score", 0),
        json.dumps(risk_card.get("checks", [])),
        risk_card.get("explanation", ""),
        risk_card.get("diff", ""),
        risk_card.get("stdout", ""),
        json.dumps(risk_card.get("action", {})),
        execution_time
    ))
    conn.commit()
    conn.close()
    return request_id


def get_history(limit: int = 50) -> List[Dict]:
    """Get recent risk cards from history."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("""
        SELECT request_id, timestamp, status, risk_score, checks, explanation, 
               diff, stdout, action, approved, approved_by, approved_at, execution_time
        FROM risk_cards
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    
    results = []
    for row in cursor.fetchall():
        results.append({
            "request_id": row[0],
            "timestamp": row[1],
            "status": row[2],
            "risk_score": row[3],
            "checks": json.loads(row[4]) if row[4] else [],
            "explanation": row[5],
            "diff": row[6],
            "stdout": row[7],
            "action": json.loads(row[8]) if row[8] else {},
            "approved": bool(row[9]),
            "approved_by": row[10],
            "approved_at": row[11],
            "execution_time": row[12]
        })
    conn.close()
    return results


def get_risk_card(request_id: str) -> Optional[Dict]:
    """Get a specific risk card by request_id."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("""
        SELECT request_id, timestamp, status, risk_score, checks, explanation,
               diff, stdout, action, approved, approved_by, approved_at, execution_time
        FROM risk_cards
        WHERE request_id = ?
    """, (request_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return {
        "request_id": row[0],
        "timestamp": row[1],
        "status": row[2],
        "risk_score": row[3],
        "checks": json.loads(row[4]) if row[4] else [],
        "explanation": row[5],
        "diff": row[6],
        "stdout": row[7],
        "action": json.loads(row[8]) if row[8] else {},
        "approved": bool(row[9]),
        "approved_by": row[10],
        "approved_at": row[11],
        "execution_time": row[12]
    }


def approve_risk_card(request_id: str, approved_by: str = "user") -> bool:
    """Approve a blocked risk card."""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("""
        UPDATE risk_cards
        SET approved = 1, approved_by = ?, approved_at = ?
        WHERE request_id = ?
    """, (approved_by, time.time(), request_id))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


# Initialize on import
init_db()

