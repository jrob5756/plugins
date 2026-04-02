"""Messages commands — get, store, cleanup, and check freshness."""

import datetime
import json
import sys

from .db import get_db, json_output, error_output, row_to_dict, init_schema, utcnow, freshness_label


def cmd_messages(args):
    action = args.msg_action
    if action == "get":
        return _messages_get(args)
    if action == "store":
        return _messages_store(args)
    if action == "cleanup":
        return _messages_cleanup(args)
    if action == "freshness":
        return _messages_freshness(args)
    error_output(f"Unknown messages action: {action}")


def _messages_get(args):
    conn = get_db()
    init_schema(conn)
    source = args.msg_source
    limit = args.limit or 50
    query = "SELECT * FROM messages WHERE source_label = ?"
    params: list = [source]
    if args.since:
        query += " AND timestamp >= ?"
        params.append(args.since)
    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)
    rows = conn.execute(query, params).fetchall()

    meta = conn.execute("SELECT * FROM sync_meta WHERE source_label = ?", (source,)).fetchone()
    conn.close()

    lf = meta["last_fetched"] if meta else None
    label, age = freshness_label(lf)
    result = {
        "source_label": source,
        "last_fetched": lf,
        "freshness": label,
        "messages": [row_to_dict(r) for r in rows],
    }
    if age is not None:
        result["age_minutes"] = age
    json_output(result)


def _messages_store(args):
    source = args.msg_source
    raw = sys.stdin.read()
    try:
        messages = json.loads(raw)
    except json.JSONDecodeError as exc:
        error_output(f"Invalid JSON on stdin: {exc}")

    conn = get_db()
    init_schema(conn)
    count = 0
    for m in messages:
        conn.execute(
            "INSERT OR REPLACE INTO messages (id, source_label, sender, content, timestamp, raw_html) VALUES (?,?,?,?,?,?)",
            (m.get("id", ""), source, m.get("sender", ""),
             m.get("content", ""), m.get("timestamp", ""), m.get("raw_html")),
        )
        count += 1
    conn.execute(
        "INSERT OR REPLACE INTO sync_meta (source_label, last_fetched, message_count) VALUES (?,?,?)",
        (source, utcnow(), count),
    )
    conn.commit()
    conn.close()
    json_output({"stored": count, "source_label": source})


def _messages_cleanup(args):
    days = args.days or 10
    cutoff = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days)).isoformat()
    conn = get_db()
    init_schema(conn)
    cur = conn.execute("DELETE FROM messages WHERE timestamp < ?", (cutoff,))
    conn.commit()
    conn.close()
    json_output({"deleted": cur.rowcount, "cutoff": cutoff})


def _messages_freshness(args):
    source = args.msg_source
    conn = get_db()
    init_schema(conn)
    meta = conn.execute("SELECT * FROM sync_meta WHERE source_label = ?", (source,)).fetchone()
    conn.close()
    lf = meta["last_fetched"] if meta else None
    label, age = freshness_label(lf)
    result = {"source_label": source, "last_fetched": lf, "freshness": label}
    if age is not None:
        result["age_minutes"] = age
    json_output(result)
