"""Sync commands — check freshness status for favorites."""

from .db import get_db, json_output, error_output, init_schema, freshness_label


def cmd_sync(args):
    action = args.sync_action
    if action == "status":
        return _sync_status(needed_only=False)
    if action == "needed":
        return _sync_status(needed_only=True)
    error_output(f"Unknown sync action: {action}")


def _sync_status(needed_only: bool):
    conn = get_db()
    init_schema(conn)
    favs = conn.execute("SELECT label, type FROM favorites ORDER BY added_at").fetchall()
    results = []
    for f in favs:
        meta = conn.execute(
            "SELECT last_fetched FROM sync_meta WHERE source_label = ?", (f["label"],)
        ).fetchone()
        lf = meta["last_fetched"] if meta else None
        label, age = freshness_label(lf)
        entry = {
            "label": f["label"],
            "type": f["type"],
            "freshness": label,
            "last_fetched": lf,
            "age_minutes": age,
        }
        if needed_only and label in ("fresh",):
            continue
        results.append(entry)
    conn.close()
    json_output(results)
