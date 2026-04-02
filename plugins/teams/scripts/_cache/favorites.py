"""Favorites commands — manage favorite chats/channels."""

from .db import get_db, json_output, error_output, row_to_dict, init_schema, utcnow


def cmd_favorites(args):
    action = args.fav_action
    if action == "list":
        return _favorites_list()
    if action == "add":
        return _favorites_add(args.fav_label, args.type)
    if action == "remove":
        return _favorites_remove(args.fav_label)
    error_output(f"Unknown favorites action: {action}")


def _favorites_list():
    conn = get_db()
    init_schema(conn)
    rows = conn.execute("SELECT label, type, added_at FROM favorites ORDER BY added_at").fetchall()
    conn.close()
    json_output([row_to_dict(r) for r in rows])


def _favorites_add(label: str, ftype: str):
    if not ftype:
        error_output("--type is required (chat or channel)")
    conn = get_db()
    init_schema(conn)
    conn.execute(
        "INSERT OR REPLACE INTO favorites (label, type, added_at) VALUES (?,?,?)",
        (label, ftype, utcnow()),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM favorites WHERE label = ?", (label,)).fetchone()
    conn.close()
    json_output(row_to_dict(row))


def _favorites_remove(label: str):
    conn = get_db()
    init_schema(conn)
    conn.execute("DELETE FROM favorites WHERE label = ?", (label,))
    conn.commit()
    conn.close()
    json_output({"removed": label})
