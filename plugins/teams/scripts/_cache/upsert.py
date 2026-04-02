"""Upsert commands — insert or update cached records."""

import json

from .db import get_db, json_output, error_output, row_to_dict, init_schema, utcnow


def cmd_upsert(args):
    target = args.upsert_target
    if target == "me":
        return _upsert_me(args)
    if target == "user":
        return _upsert_user(args)
    if target == "chat":
        return _upsert_chat(args)
    if target == "team":
        return _upsert_team(args)
    if target == "channel":
        return _upsert_channel(args)
    error_output(f"Unknown upsert target: {target}")


def _upsert_me(args):
    conn = get_db()
    init_schema(conn)
    conn.execute(
        "INSERT OR REPLACE INTO me (id, display_name, upn, user_id, timezone, updated_at) VALUES (1,?,?,?,?,?)",
        (args.name, args.upn, args.user_id, args.timezone, utcnow()),
    )
    conn.commit()
    row = conn.execute("SELECT display_name, upn, user_id, timezone, updated_at FROM me WHERE id=1").fetchone()
    conn.close()
    json_output(row_to_dict(row))


def _upsert_user(args):
    conn = get_db()
    init_schema(conn)
    conn.execute(
        "INSERT OR REPLACE INTO users (display_name, upn, user_id, updated_at) VALUES (?,?,?,?)",
        (args.upsert_key, args.upn, args.user_id, utcnow()),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM users WHERE display_name = ?", (args.upsert_key,)).fetchone()
    conn.close()
    json_output(row_to_dict(row))


def _upsert_chat(args):
    conn = get_db()
    init_schema(conn)
    conn.execute(
        "INSERT OR REPLACE INTO chats (label, chat_id, type, team_name, team_id, updated_at) VALUES (?,?,?,?,?,?)",
        (args.upsert_key, args.chat_id, args.type, args.team, args.team_id, utcnow()),
    )
    if args.members:
        members = json.loads(args.members)
        conn.execute("DELETE FROM chat_members WHERE chat_label = ?", (args.upsert_key,))
        for m in members:
            conn.execute(
                "INSERT OR IGNORE INTO chat_members (chat_label, display_name) VALUES (?,?)",
                (args.upsert_key, m),
            )
    conn.commit()
    row = conn.execute("SELECT * FROM chats WHERE label = ?", (args.upsert_key,)).fetchone()
    members = conn.execute(
        "SELECT display_name FROM chat_members WHERE chat_label = ?", (args.upsert_key,)
    ).fetchall()
    conn.close()
    result = row_to_dict(row)
    result["members"] = [m["display_name"] for m in members]
    json_output(result)


def _upsert_team(args):
    conn = get_db()
    init_schema(conn)
    conn.execute(
        "INSERT OR REPLACE INTO teams (team_name, team_id, updated_at) VALUES (?,?,?)",
        (args.upsert_key, args.team_id, utcnow()),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM teams WHERE team_name = ?", (args.upsert_key,)).fetchone()
    conn.close()
    json_output(row_to_dict(row))


def _upsert_channel(args):
    conn = get_db()
    init_schema(conn)
    team_row = conn.execute("SELECT team_name FROM teams WHERE team_name = ?", (args.upsert_key,)).fetchone()
    if not team_row:
        conn.close()
        error_output(f"Team '{args.upsert_key}' not found — upsert the team first.")
    conn.execute(
        "INSERT OR REPLACE INTO channels (team_name, channel_name, channel_id) VALUES (?,?,?)",
        (args.upsert_key, args.upsert_extra, args.channel_id),
    )
    conn.commit()
    row = conn.execute(
        "SELECT c.team_name, t.team_id, c.channel_name, c.channel_id FROM channels c "
        "JOIN teams t ON c.team_name = t.team_name "
        "WHERE c.team_name = ? AND c.channel_name = ?",
        (args.upsert_key, args.upsert_extra),
    ).fetchone()
    conn.close()
    json_output(row_to_dict(row))
