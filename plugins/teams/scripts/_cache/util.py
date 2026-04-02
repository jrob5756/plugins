"""Utility commands — clean-html, stats, export, reset."""

import html
import re
import sys

from .db import get_db, json_output, error_output, row_to_dict, init_schema


def cmd_util(args):
    action = args.util_action
    if action == "clean-html":
        return _util_clean_html()
    error_output(f"Unknown util action: {action}")


def _util_clean_html():
    raw = sys.stdin.read()
    text = raw

    # Code blocks first (preserve content)
    text = re.sub(r'<codeblock>\s*<code[^>]*>', '\n```\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</code>\s*</codeblock>', '\n```\n', text, flags=re.IGNORECASE)

    # Headings
    text = re.sub(r'<h[12][^>]*>(.*?)</h[12]>', r'\n## \1\n', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<h[34][^>]*>(.*?)</h[34]>', r'\n### \1\n', text, flags=re.IGNORECASE | re.DOTALL)

    # Line breaks
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)

    # List items
    text = re.sub(r'<li[^>]*>(.*?)</li>', r'\n- \1', text, flags=re.IGNORECASE | re.DOTALL)

    # Paragraphs
    text = re.sub(r'<p[^>]*>(.*?)</p>', r'\1\n', text, flags=re.IGNORECASE | re.DOTALL)

    # Strip remaining tags
    text = re.sub(r'<[^>]+>', '', text)

    # Unescape HTML entities
    text = html.unescape(text)

    # Collapse 3+ newlines to 2
    text = re.sub(r'\n{3,}', '\n\n', text)

    text = text.strip() + '\n'
    sys.stdout.write(text)
    sys.exit(0)


def cmd_stats(_args):
    conn = get_db()
    init_schema(conn)
    counts = {}
    for table in ("users", "chats", "teams", "channels", "messages", "favorites"):
        counts[table] = conn.execute(f"SELECT COUNT(*) AS c FROM {table}").fetchone()["c"]  # noqa: S608
    conn.close()
    json_output(counts)


def cmd_export(_args):
    conn = get_db()
    init_schema(conn)
    data: dict = {}

    me_row = conn.execute("SELECT * FROM me WHERE id=1").fetchone()
    data["me"] = row_to_dict(me_row) if me_row else None

    for table in ("users", "chats", "chat_members", "teams", "channels",
                   "favorites", "messages", "sync_meta"):
        rows = conn.execute(f"SELECT * FROM {table}").fetchall()  # noqa: S608
        data[table] = [row_to_dict(r) for r in rows]
    conn.close()
    json_output(data)


def cmd_reset(_args):
    conn = get_db()
    for table in ("chat_members", "channels", "messages", "sync_meta",
                   "favorites", "chats", "teams", "users", "me"):
        conn.execute(f"DROP TABLE IF EXISTS {table}")  # noqa: S608
    conn.commit()
    init_schema(conn)
    conn.close()
    json_output({"reset": True})
