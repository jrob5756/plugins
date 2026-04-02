"""Lookup commands — read cached records by name/label."""

from .db import get_db, json_output, error_output, row_to_dict


def cmd_lookup(args):
    target = args.lookup_target
    if target == "me":
        return _lookup_me()
    if target == "user":
        return _lookup_user(args.lookup_key)
    if target == "chat":
        return _lookup_chat(args.lookup_key)
    if target == "team":
        return _lookup_team(args.lookup_key)
    if target == "channel":
        return _lookup_channel(args.lookup_key, args.lookup_extra)
    error_output(f"Unknown lookup target: {target}")


def _lookup_me():
    conn = get_db()
    row = conn.execute("SELECT display_name, upn, user_id, timezone, updated_at FROM me WHERE id=1").fetchone()
    conn.close()
    if not row:
        json_output({"error": "not_found", "query": "me", "source": "cache"}, 1)
    json_output({**row_to_dict(row), "source": "cache"})


def _lookup_user(name: str):
    conn = get_db()
    # exact (case-insensitive)
    rows = conn.execute(
        "SELECT display_name, upn, user_id FROM users WHERE lower(display_name) = lower(?)", (name,)
    ).fetchall()
    if not rows:
        # substring
        rows = conn.execute(
            "SELECT display_name, upn, user_id FROM users WHERE lower(display_name) LIKE '%' || lower(?) || '%'",
            (name,),
        ).fetchall()
    conn.close()
    if not rows:
        json_output({"error": "not_found", "query": name, "source": "cache"}, 1)
    results = [{**row_to_dict(r), "source": "cache"} for r in rows]
    json_output(results[0] if len(results) == 1 else results)


def _lookup_chat(label: str):
    conn = get_db()
    rows = conn.execute(
        "SELECT label, chat_id, type, team_name, team_id FROM chats WHERE lower(label) = lower(?)", (label,)
    ).fetchall()
    if not rows:
        rows = conn.execute(
            "SELECT label, chat_id, type, team_name, team_id FROM chats WHERE lower(label) LIKE '%' || lower(?) || '%'",
            (label,),
        ).fetchall()
    conn.close()
    if not rows:
        json_output({"error": "not_found", "query": label, "source": "cache"}, 1)

    results = []
    conn = get_db()
    for r in rows:
        d = {**row_to_dict(r), "source": "cache"}
        members = conn.execute(
            "SELECT display_name FROM chat_members WHERE chat_label = ?", (r["label"],)
        ).fetchall()
        d["members"] = [m["display_name"] for m in members]
        results.append(d)
    conn.close()
    json_output(results[0] if len(results) == 1 else results)


def _lookup_team(name: str):
    conn = get_db()
    rows = conn.execute(
        "SELECT team_name, team_id FROM teams WHERE lower(team_name) = lower(?)", (name,)
    ).fetchall()
    if not rows:
        rows = conn.execute(
            "SELECT team_name, team_id FROM teams WHERE lower(team_name) LIKE '%' || lower(?) || '%'", (name,)
        ).fetchall()
    if not rows:
        conn.close()
        json_output({"error": "not_found", "query": name, "source": "cache"}, 1)

    results = []
    for r in rows:
        d = {**row_to_dict(r), "source": "cache"}
        channels = conn.execute(
            "SELECT channel_name, channel_id FROM channels WHERE team_name = ?", (r["team_name"],)
        ).fetchall()
        d["channels"] = [row_to_dict(c) for c in channels]
        results.append(d)
    conn.close()
    json_output(results[0] if len(results) == 1 else results)


def _lookup_channel(team: str, channel: str):
    if not channel:
        error_output("Usage: lookup channel <team> <channel>")
    conn = get_db()
    # exact
    row = conn.execute(
        "SELECT c.team_name, t.team_id, c.channel_name, c.channel_id FROM channels c "
        "JOIN teams t ON c.team_name = t.team_name "
        "WHERE lower(c.team_name) = lower(?) AND lower(c.channel_name) = lower(?)",
        (team, channel),
    ).fetchone()
    if not row:
        # fuzzy
        row = conn.execute(
            "SELECT c.team_name, t.team_id, c.channel_name, c.channel_id FROM channels c "
            "JOIN teams t ON c.team_name = t.team_name "
            "WHERE lower(c.team_name) LIKE '%' || lower(?) || '%' "
            "AND lower(c.channel_name) LIKE '%' || lower(?) || '%'",
            (team, channel),
        ).fetchone()
    conn.close()
    if not row:
        json_output({"error": "not_found", "query": {"team": team, "channel": channel}, "source": "cache"}, 1)
    json_output({**row_to_dict(row), "source": "cache"})
