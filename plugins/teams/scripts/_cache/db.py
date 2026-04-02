"""Database helpers, schema, and shared utilities."""

import datetime
import json
import pathlib
import sqlite3
import sys

DB_DIR = pathlib.Path.home() / ".local" / "share" / "teams-mcp-cache"
DB_PATH = DB_DIR / "teams-cache.db"

SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS me (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    display_name TEXT NOT NULL,
    upn TEXT NOT NULL,
    user_id TEXT NOT NULL,
    timezone TEXT,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS users (
    display_name TEXT PRIMARY KEY,
    upn TEXT NOT NULL,
    user_id TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_users_upn ON users(upn);
CREATE INDEX IF NOT EXISTS idx_users_name_lower ON users(lower(display_name));

CREATE TABLE IF NOT EXISTS chats (
    label TEXT PRIMARY KEY,
    chat_id TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL CHECK (type IN ('oneOnOne', 'group', 'channel', 'meeting', 'self')),
    team_name TEXT,
    team_id TEXT,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS chat_members (
    chat_label TEXT NOT NULL REFERENCES chats(label) ON DELETE CASCADE,
    display_name TEXT NOT NULL,
    PRIMARY KEY (chat_label, display_name)
);

CREATE TABLE IF NOT EXISTS teams (
    team_name TEXT PRIMARY KEY,
    team_id TEXT NOT NULL UNIQUE,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS channels (
    team_name TEXT NOT NULL REFERENCES teams(team_name) ON DELETE CASCADE,
    channel_name TEXT NOT NULL,
    channel_id TEXT NOT NULL,
    PRIMARY KEY (team_name, channel_name)
);

CREATE TABLE IF NOT EXISTS favorites (
    label TEXT PRIMARY KEY,
    type TEXT NOT NULL CHECK (type IN ('chat', 'channel')),
    added_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS messages (
    id TEXT NOT NULL,
    source_label TEXT NOT NULL,
    sender TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    raw_html TEXT,
    PRIMARY KEY (source_label, id)
);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_messages_source ON messages(source_label, timestamp);

CREATE TABLE IF NOT EXISTS sync_meta (
    source_label TEXT PRIMARY KEY,
    last_fetched TEXT NOT NULL,
    message_count INTEGER DEFAULT 0
);
"""


def get_db() -> sqlite3.Connection:
    """Return a connection with WAL mode and foreign keys enabled."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def json_output(data, exit_code: int = 0):
    """Print *data* as JSON to stdout and exit."""
    print(json.dumps(data, indent=2, default=str))
    sys.exit(exit_code)


def error_output(message: str, exit_code: int = 2):
    """Print an error object to stderr and exit."""
    print(json.dumps({"error": message}), file=sys.stderr)
    sys.exit(exit_code)


def row_to_dict(row: sqlite3.Row) -> dict:
    return dict(row) if row else {}


def utcnow() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def freshness_label(last_fetched: str | None):
    """Return (label, age_minutes) from an ISO timestamp."""
    if not last_fetched:
        return "unknown", None
    try:
        dt = datetime.datetime.fromisoformat(last_fetched.replace("Z", "+00:00"))
    except Exception:
        try:
            dt = datetime.datetime.strptime(last_fetched, "%Y-%m-%d %H:%M:%S")
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        except Exception:
            return "unknown", None
    now = datetime.datetime.now(datetime.timezone.utc)
    age = (now - dt).total_seconds() / 60.0
    if age < 15:
        return "fresh", round(age, 1)
    if age < 60:
        return "stale", round(age, 1)
    return "expired", round(age, 1)


def init_schema(conn: sqlite3.Connection):
    """Execute the full schema (idempotent)."""
    conn.executescript(SCHEMA_SQL)


def cleanup_old_messages(conn: sqlite3.Connection, days: int = 10) -> int:
    cutoff = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days)).isoformat()
    cur = conn.execute("DELETE FROM messages WHERE timestamp < ?", (cutoff,))
    conn.commit()
    return cur.rowcount


def cmd_init(_args):
    """Initialize the cache database and clean old messages."""
    conn = get_db()
    init_schema(conn)
    deleted = cleanup_old_messages(conn)
    conn.close()
    json_output({"initialized": True, "db": str(DB_PATH), "old_messages_cleaned": deleted})
