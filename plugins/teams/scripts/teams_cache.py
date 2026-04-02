#!/usr/bin/env python3
"""Teams MCP cache CLI — manages a local SQLite cache for Teams lookups.

Usage: python3 teams_cache.py <command> [args]
All output is JSON (stdout), errors go to stderr.
Exit codes: 0=success, 1=not found, 2=error.
"""

import argparse
import os
import sqlite3
import sys

# Ensure _cache package is importable regardless of cwd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _cache.db import error_output
from _cache.favorites import cmd_favorites
from _cache.lookup import cmd_lookup
from _cache.messages import cmd_messages
from _cache.db import cmd_init
from _cache.sync import cmd_sync
from _cache.upsert import cmd_upsert
from _cache.util import cmd_export, cmd_reset, cmd_stats, cmd_util


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="teams_cache",
        description="Teams MCP local cache CLI (SQLite-backed)",
    )
    sub = parser.add_subparsers(dest="command")

    # init
    sub.add_parser("init", help="Initialize the cache database")

    # lookup
    p_lookup = sub.add_parser("lookup", help="Look up cached records")
    p_lookup.add_argument("lookup_target", choices=["me", "user", "chat", "team", "channel"])
    p_lookup.add_argument("lookup_key", nargs="?", default="")
    p_lookup.add_argument("lookup_extra", nargs="?", default="")

    # upsert
    p_upsert = sub.add_parser("upsert", help="Insert or update cached records")
    p_upsert.add_argument("upsert_target", choices=["me", "user", "chat", "team", "channel"])
    p_upsert.add_argument("upsert_key", nargs="?", default="")
    p_upsert.add_argument("upsert_extra", nargs="?", default="")
    p_upsert.add_argument("--upn", default="")
    p_upsert.add_argument("--user-id", dest="user_id", default="")
    p_upsert.add_argument("--name", dest="name", default="")
    p_upsert.add_argument("--timezone", default=None)
    p_upsert.add_argument("--chat-id", dest="chat_id", default="")
    p_upsert.add_argument("--type", dest="type", default="oneOnOne")
    p_upsert.add_argument("--members", default=None)
    p_upsert.add_argument("--team", default=None)
    p_upsert.add_argument("--team-id", dest="team_id", default="")
    p_upsert.add_argument("--channel-id", dest="channel_id", default="")

    # favorites
    p_fav = sub.add_parser("favorites", help="Manage favorites")
    p_fav.add_argument("fav_action", choices=["list", "add", "remove"])
    p_fav.add_argument("fav_label", nargs="?", default="")
    p_fav.add_argument("--type", dest="type", default="")

    # messages
    p_msg = sub.add_parser("messages", help="Manage cached messages")
    p_msg.add_argument("msg_action", choices=["get", "store", "cleanup", "freshness"])
    p_msg.add_argument("msg_source", nargs="?", default="")
    p_msg.add_argument("--limit", type=int, default=None)
    p_msg.add_argument("--since", default=None)
    p_msg.add_argument("--stdin", action="store_true")
    p_msg.add_argument("--days", type=int, default=None)

    # sync
    p_sync = sub.add_parser("sync", help="Sync status for favorites")
    p_sync.add_argument("sync_action", choices=["status", "needed"])

    # stats / export / reset
    sub.add_parser("stats", help="Show cache statistics")
    sub.add_parser("export", help="Export entire cache as JSON")
    sub.add_parser("reset", help="Drop and recreate all tables")

    # util
    p_util = sub.add_parser("util", help="Utility commands")
    p_util.add_argument("util_action", choices=["clean-html"])
    p_util.add_argument("--stdin", action="store_true")

    return parser


DISPATCH = {
    "init": cmd_init,
    "lookup": cmd_lookup,
    "upsert": cmd_upsert,
    "favorites": cmd_favorites,
    "messages": cmd_messages,
    "sync": cmd_sync,
    "stats": cmd_stats,
    "export": cmd_export,
    "reset": cmd_reset,
    "util": cmd_util,
}


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help(sys.stderr)
        sys.exit(2)

    handler = DISPATCH.get(args.command)
    if not handler:
        error_output(f"Unknown command: {args.command}")

    try:
        handler(args)
    except sqlite3.Error as exc:
        error_output(f"Database error: {exc}")
    except Exception as exc:
        error_output(f"Unexpected error: {exc}")


if __name__ == "__main__":
    main()
