"""
models.py — SQLite data-access layer with parameterised queries.
Provides CRUD for assets, threats, assessments, compliance, and notifications.
"""

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator, Optional

import config

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def _ensure_db_dir() -> None:
    """Create database directory if it does not exist."""
    db_path = Path(config.DATABASE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager yielding a SQLite connection with row factory.

    Yields:
        sqlite3.Connection with foreign keys enabled.

    Side effects:
        Opens and closes a database connection per use.
    """
    _ensure_db_dir()
    conn = sqlite3.connect(config.DATABASE_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """
    Initialise database schema from schema.sql.

    Side effects:
        Creates tables if they do not exist.
    """
    _ensure_db_dir()
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = f.read()
    with get_db() as conn:
        conn.executescript(schema)


def row_to_dict(row: Optional[sqlite3.Row]) -> Optional[dict[str, Any]]:
    """Convert sqlite3.Row to dict, or None."""
    if row is None:
        return None
    return dict(row)


# --- Assets ---


def create_asset(
    session_id: str,
    name: str,
    asset_type: str,
    value_usd: float,
    description: str = "",
    software: str = "",
) -> dict[str, Any]:
    """Insert a new asset and return the created row."""
    with get_db() as conn:
        cur = conn.execute(
            """
            INSERT INTO assets (session_id, name, asset_type, value_usd, description, software)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (session_id, name, asset_type, value_usd, description or "", software or ""),
        )
        asset_id = cur.lastrowid
        row = conn.execute("SELECT * FROM assets WHERE id = ?", (asset_id,)).fetchone()
    return row_to_dict(row)


def get_assets(session_id: str) -> list[dict[str, Any]]:
    """List all assets for a session."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM assets WHERE session_id = ? ORDER BY created_at DESC",
            (session_id,),
        ).fetchall()
    return [row_to_dict(r) for r in rows]


def get_asset(asset_id: int, session_id: Optional[str] = None) -> Optional[dict[str, Any]]:
    """Get a single asset by id, optionally scoped to session."""
    with get_db() as conn:
        if session_id:
            row = conn.execute(
                "SELECT * FROM assets WHERE id = ? AND session_id = ?",
                (asset_id, session_id),
            ).fetchone()
        else:
            row = conn.execute("SELECT * FROM assets WHERE id = ?", (asset_id,)).fetchone()
    return row_to_dict(row)


def update_asset(asset_id: int, session_id: str, **fields: Any) -> Optional[dict[str, Any]]:
    """Update asset fields; only provided kwargs are updated."""
    allowed = {"name", "asset_type", "value_usd", "description", "software"}
    updates = {k: v for k, v in fields.items() if k in allowed and v is not None}
    if not updates:
        return get_asset(asset_id, session_id)
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [asset_id, session_id]
    with get_db() as conn:
        conn.execute(
            f"UPDATE assets SET {set_clause} WHERE id = ? AND session_id = ?",
            values,
        )
        row = conn.execute(
            "SELECT * FROM assets WHERE id = ? AND session_id = ?",
            (asset_id, session_id),
        ).fetchone()
    return row_to_dict(row)


def delete_asset(asset_id: int, session_id: str) -> bool:
    """Delete asset and cascading threats."""
    with get_db() as conn:
        cur = conn.execute(
            "DELETE FROM assets WHERE id = ? AND session_id = ?",
            (asset_id, session_id),
        )
    return cur.rowcount > 0


# --- Threats ---


def create_threat(
    asset_id: int,
    name: str,
    probability: float,
    vulnerability_score: int,
    mitigation_effectiveness: float,
    aro: float,
    exposure_factor: float,
    category: str = "",
    uncertainty: float = 0.1,
    threat_level: int = 3,
) -> dict[str, Any]:
    """Insert a threat linked to an asset."""
    with get_db() as conn:
        cur = conn.execute(
            """
            INSERT INTO threats (
                asset_id, name, category, probability, vulnerability_score,
                mitigation_effectiveness, aro, exposure_factor, uncertainty, threat_level
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                asset_id,
                name,
                category or "",
                probability,
                vulnerability_score,
                mitigation_effectiveness,
                aro,
                exposure_factor,
                uncertainty,
                threat_level,
            ),
        )
        threat_id = cur.lastrowid
        row = conn.execute("SELECT * FROM threats WHERE id = ?", (threat_id,)).fetchone()
    return row_to_dict(row)


def get_threats(session_id: Optional[str] = None, asset_id: Optional[int] = None) -> list[dict[str, Any]]:
    """List threats, optionally filtered by session or asset."""
    with get_db() as conn:
        if asset_id:
            rows = conn.execute(
                "SELECT t.* FROM threats t JOIN assets a ON t.asset_id = a.id WHERE t.asset_id = ?",
                (asset_id,),
            ).fetchall()
        elif session_id:
            rows = conn.execute(
                """
                SELECT t.* FROM threats t
                JOIN assets a ON t.asset_id = a.id
                WHERE a.session_id = ?
                ORDER BY t.created_at DESC
                """,
                (session_id,),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM threats ORDER BY created_at DESC").fetchall()
    return [row_to_dict(r) for r in rows]


def get_threat(threat_id: int) -> Optional[dict[str, Any]]:
    """Get a single threat by id."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM threats WHERE id = ?", (threat_id,)).fetchone()
    return row_to_dict(row)


def update_threat(threat_id: int, **fields: Any) -> Optional[dict[str, Any]]:
    """Update threat fields."""
    allowed = {
        "name",
        "category",
        "probability",
        "vulnerability_score",
        "mitigation_effectiveness",
        "aro",
        "exposure_factor",
        "uncertainty",
        "threat_level",
        "asset_id",
    }
    updates = {k: v for k, v in fields.items() if k in allowed and v is not None}
    if not updates:
        return get_threat(threat_id)
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [threat_id]
    with get_db() as conn:
        conn.execute(f"UPDATE threats SET {set_clause} WHERE id = ?", values)
        row = conn.execute("SELECT * FROM threats WHERE id = ?", (threat_id,)).fetchone()
    return row_to_dict(row)


def delete_threat(threat_id: int) -> bool:
    """Delete a threat by id."""
    with get_db() as conn:
        cur = conn.execute("DELETE FROM threats WHERE id = ?", (threat_id,))
    return cur.rowcount > 0


def get_assets_with_threats(session_id: str) -> list[dict[str, Any]]:
    """Return assets each with nested threats list for assessment."""
    assets = get_assets(session_id)
    for asset in assets:
        asset["threats"] = get_threats(asset_id=asset["id"])
    return assets


# --- Assessments ---


def save_assessment(
    session_id: str,
    results: dict[str, Any],
    llm_recommendations: Optional[str] = None,
) -> dict[str, Any]:
    """Persist assessment results as JSON."""
    results_json = json.dumps(results)
    with get_db() as conn:
        cur = conn.execute(
            """
            INSERT INTO assessments (session_id, results_json, llm_recommendations)
            VALUES (?, ?, ?)
            """,
            (session_id, results_json, llm_recommendations),
        )
        aid = cur.lastrowid
        row = conn.execute("SELECT * FROM assessments WHERE id = ?", (aid,)).fetchone()
    result = row_to_dict(row)
    if result and result.get("results_json"):
        result["results"] = json.loads(result["results_json"])
    return result


def get_latest_assessment(session_id: str) -> Optional[dict[str, Any]]:
    """Get most recent assessment for session."""
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT * FROM assessments
            WHERE session_id = ?
            ORDER BY created_at DESC LIMIT 1
            """,
            (session_id,),
        ).fetchone()
    if not row:
        return None
    result = row_to_dict(row)
    if result.get("results_json"):
        result["results"] = json.loads(result["results_json"])
    if result.get("llm_recommendations"):
        try:
            result["llm_recommendations_parsed"] = json.loads(result["llm_recommendations"])
        except json.JSONDecodeError:
            pass
    return result


# --- Compliance ---


def upsert_compliance(
    session_id: str,
    control_id: str,
    control_name: str,
    status: str,
    notes: str = "",
) -> dict[str, Any]:
    """Insert or update compliance control status."""
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO compliance_status (session_id, control_id, control_name, status, notes)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(session_id, control_id) DO UPDATE SET
                status = excluded.status,
                control_name = excluded.control_name,
                notes = excluded.notes
            """,
            (session_id, control_id, control_name, status, notes or ""),
        )
        row = conn.execute(
            "SELECT * FROM compliance_status WHERE session_id = ? AND control_id = ?",
            (session_id, control_id),
        ).fetchone()
    return row_to_dict(row)


def get_compliance(session_id: str) -> list[dict[str, Any]]:
    """List all compliance records for session."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM compliance_status WHERE session_id = ? ORDER BY control_id",
            (session_id,),
        ).fetchall()
    return [row_to_dict(r) for r in rows]


# --- Notifications ---


def add_notification(
    session_id: Optional[str],
    message: str,
    severity: str = "info",
) -> dict[str, Any]:
    """Add a dashboard notification."""
    with get_db() as conn:
        cur = conn.execute(
            """
            INSERT INTO notifications (session_id, message, severity)
            VALUES (?, ?, ?)
            """,
            (session_id, message, severity),
        )
        nid = cur.lastrowid
        row = conn.execute("SELECT * FROM notifications WHERE id = ?", (nid,)).fetchone()
    return row_to_dict(row)


def get_notifications(session_id: Optional[str] = None, unread_only: bool = False) -> list[dict[str, Any]]:
    """List notifications."""
    with get_db() as conn:
        query = "SELECT * FROM notifications WHERE 1=1"
        params: list[Any] = []
        if session_id:
            query += " AND (session_id = ? OR session_id IS NULL)"
            params.append(session_id)
        if unread_only:
            query += " AND read_flag = 0"
        query += " ORDER BY created_at DESC LIMIT 50"
        rows = conn.execute(query, params).fetchall()
    return [row_to_dict(r) for r in rows]


# --- Assessment History ---


def get_all_assessments(session_id: str) -> list[dict[str, Any]]:
    """List all assessments for session, newest first, with parsed summaries."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, session_id, created_at, results_json FROM assessments "
            "WHERE session_id = ? ORDER BY created_at DESC",
            (session_id,),
        ).fetchall()
    result = []
    for r in rows:
        d = row_to_dict(r)
        if d and d.get("results_json"):
            try:
                parsed = json.loads(d["results_json"])
                d["results"] = parsed
                d["summary"] = parsed.get("summary", {})
            except Exception:
                d["summary"] = {}
        result.append(d)
    return result


# --- Treatment Plans ---


def upsert_treatment_plan(
    session_id: str,
    asset_name: str,
    threat_name: str,
    strategy: str = "Mitigate",
    owner: str = "",
    due_date: str = "",
    status: str = "Pending",
    notes: str = "",
) -> dict[str, Any]:
    """Insert or update a treatment plan entry for a risk."""
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO treatment_plans
                (session_id, asset_name, threat_name, strategy, owner, due_date, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(session_id, asset_name, threat_name) DO UPDATE SET
                strategy   = excluded.strategy,
                owner      = excluded.owner,
                due_date   = excluded.due_date,
                status     = excluded.status,
                notes      = excluded.notes,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                session_id, asset_name, threat_name,
                strategy, owner or "", due_date or "", status, notes or "",
            ),
        )
        row = conn.execute(
            "SELECT * FROM treatment_plans "
            "WHERE session_id = ? AND asset_name = ? AND threat_name = ?",
            (session_id, asset_name, threat_name),
        ).fetchone()
    return row_to_dict(row)


def get_treatment_plans(session_id: str) -> list[dict[str, Any]]:
    """List all treatment plans for a session."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM treatment_plans WHERE session_id = ? ORDER BY updated_at DESC",
            (session_id,),
        ).fetchall()
    return [row_to_dict(r) for r in rows]
