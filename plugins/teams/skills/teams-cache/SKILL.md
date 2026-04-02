---
name: teams-cache
description: |
  Teams MCP efficiency layer with SQLite-backed caching of user UPNs, chat IDs, team IDs,
  channel IDs, and messages. Provides a Python CLI for instant lookups and cache management.
  ALWAYS use this skill for ANY Teams operation — sending messages, reading chats, posting
  to channels, looking up users. This skill MUST be activated before calling ANY Teams MCP
  tool. Triggers: send message, read message, message someone, chat with, reply to, post
  to channel, teams, teams chat, teams lookup, teams user, list teams chats, teams channel,
  teams meeting, sync favorites, teams cache. Always invoke first to check the local cache
  and avoid redundant API lookups.
user-invocable: false
---

# Teams Cache — Efficient Teams MCP Usage

SQLite-backed cache at `~/.local/share/teams-mcp-cache/teams-cache.db` that stores user UPNs, chat IDs, team/channel IDs, and recent messages. Managed entirely through the `teams_cache.py` CLI — never read or write the database directly.

## Script Location

```bash
# Set this once per session — all examples below use $CACHE_SCRIPT
CACHE_SCRIPT="plugins/teams/scripts/teams_cache.py"
```

Resolve the full path relative to the workspace root. All commands follow the pattern:

```bash
python3 "$CACHE_SCRIPT" <command> [args...]
```

## Auto-Sync on Activation (MANDATORY)

When this skill is activated, **immediately** launch a background agent (teams agent) to sync all stale or unknown favorites. Do NOT wait for the user to ask — this is automatic.

```
1. python3 "$CACHE_SCRIPT" sync needed       → check which favorites need syncing
2. If ANY favorites show freshness "unknown" or "stale":
   → Launch a background teams agent to sync ALL of them
   → For each: fetch messages via MCP, then store with `messages store`
   → Do NOT block the main conversation — use mode: "background"
3. If all favorites are "fresh" → skip, no sync needed
```

This ensures cached messages are always available for fast lookups without the user having to request it.

## Cache-First Workflow

Execute this pattern before EVERY Teams MCP tool call:

```
1. python3 "$CACHE_SCRIPT" lookup <type> <name>
2. HIT  → use returned identifiers directly in the MCP call
3. MISS → call the Teams MCP API → then:
   python3 "$CACHE_SCRIPT" upsert <type> <name> --upn=... --user-id=...
```

Never skip step 1. Never call a Teams MCP tool without checking the cache first.

## Quick Command Reference

| Task | Command |
|------|---------|
| Find a user | `python3 "$CACHE_SCRIPT" lookup user "Lucio"` |
| Find a chat | `python3 "$CACHE_SCRIPT" lookup chat "Lucio"` |
| Find a team | `python3 "$CACHE_SCRIPT" lookup team "SoftwareEE"` |
| Find a channel | `python3 "$CACHE_SCRIPT" lookup channel "SoftwareEE" "General"` |
| Get my identity | `python3 "$CACHE_SCRIPT" lookup me` |
| Cache a new user | `python3 "$CACHE_SCRIPT" upsert user "Name" --upn=user@domain.com --user-id=GUID` |
| Cache a new chat | `python3 "$CACHE_SCRIPT" upsert chat "Label" --chat-id=19:...@thread.v2 --type=oneOnOne --members='["A","B"]'` |
| Add favorite | `python3 "$CACHE_SCRIPT" favorites add "Label" --type=chat` |
| List favorites | `python3 "$CACHE_SCRIPT" favorites list` |
| Get cached messages | `python3 "$CACHE_SCRIPT" messages get "Label" --limit=20` |
| Store messages | `echo '<json>' \| python3 "$CACHE_SCRIPT" messages store "Label" --stdin` |
| Check what needs sync | `python3 "$CACHE_SCRIPT" sync needed` |
| Clean HTML | `echo '<html>' \| python3 "$CACHE_SCRIPT" util clean-html --stdin` |
| Cache stats | `python3 "$CACHE_SCRIPT" stats` |

## Common Operations

### Send a message to someone

```
1. python3 "$CACHE_SCRIPT" lookup user "Lucio"        → get UPN
2. python3 "$CACHE_SCRIPT" lookup chat "Lucio"         → get chatId
3. PostMessage(chatId=..., content="Hello!")
```

If step 2 misses, call `ListChats` with the UPN from step 1, then upsert the chat.

### Post to a channel

```
1. python3 "$CACHE_SCRIPT" lookup channel "SoftwareEE" "General"  → get teamId + channelId
2. PostChannelMessage(teamId=..., channelId=..., content="Update")
```

If step 1 misses, call `ListTeams` → `ListChannels`, then upsert.

### Read chat messages

```
1. KEYWORD CHECK: If user says "latest", "new", "just got", "recent", "unread"
   → SKIP cache, go directly to step 3
2. python3 "$CACHE_SCRIPT" messages freshness "Lucio"   → check staleness (fresh = <5 min)
   If fresh → python3 "$CACHE_SCRIPT" messages get "Lucio" --limit=20
3. If stale/expired/unknown/keyword bypass → lookup chat → ListChatMessages →
   IMMEDIATELY cache: echo '[...]' | python3 "$CACHE_SCRIPT" messages store "Lucio" --stdin
```

**CRITICAL: ALWAYS cache messages after fetching them.** Never skip this step.

### Read channel messages

Same as chat messages, plus: always pipe body content through `util clean-html`.

```
1. python3 "$CACHE_SCRIPT" messages get "SoftwareEE/General" --limit=20
2. If stale → fetch via ListChannelMessages → store → clean HTML before presenting
3. echo "$body_html" | python3 "$CACHE_SCRIPT" util clean-html --stdin
```

## Favorites & Message Caching

Favorites are chats and channels you want messages automatically cached for.

- Add with `favorites add "Label" --type=chat` (or `--type=channel`)
- Last 10 days of messages are stored; older messages are auto-cleaned
- Stale favorites are auto-synced when the skill activates (see Auto-Sync above)
- Refresh stale entries by fetching via MCP tools and piping to `messages store`

## Background Agent Patterns

Use background agents for non-blocking cache operations:

- **Session-start**: init cache + sync stale favorites in a background agent
- **Parallel lookups**: launch multiple `lookup` calls simultaneously for batch operations
- **Non-blocking refresh**: return cached data immediately, refresh in background

→ See `references/background-agents.md` for detailed orchestration patterns.

## User Cache Miss Resolution

When `lookup user` returns no result, resolve in this priority order:

**Method 1: SearchTeamMessagesQueryParameters (preferred)**

```
queryString: "from:FirstName LastName"
size: 3
```

Extract from the response:
- `from.emailAddress.name` → display name
- `from.emailAddress.address` → UPN
- `chatId` → chat ID

This resolves the user, their UPN, AND the chat ID in one call.

**Method 2: SearchTeamsMessages (natural language fallback)**

```
message: "messages from FirstName LastName"
```

Parse the response for user identity and chat context.

**After resolving, always upsert BOTH user and chat:**

```bash
python3 "$CACHE_SCRIPT" upsert user "Display Name" --upn=user@domain.com --user-id=GUID
python3 "$CACHE_SCRIPT" upsert chat "Display Name" --chat-id=19:...@thread.v2 --type=oneOnOne --members='["Me","Display Name"]'
```

## Channel Messages

Channel messages differ from chat messages in critical ways:

- **Always HTML** — pipe every channel message body through `util clean-html` before presenting
- **Flat sender structure** — use `from.displayName` (not `from.user.displayName`)
- **`body.contentType`** — always `"Html"`, never `"Text"`
- **Thread replies** — `ListChannelMessages` returns only top-level posts; use the Graph API fetch-replies script (defined in agent instructions) for threaded replies

→ See `references/html-cleanup.md` for HTML-to-markdown conversion details.

## Performance Impact

| Operation | Without Cache | With Cache |
|-----------|--------------|------------|
| Send message to "Lucio" | ListChats (2000+ results) → scan → PostMessage | `lookup chat` → PostMessage |
| Post to "General" channel | ListTeams → ListChannels → PostChannelMessage | `lookup channel` → PostChannelMessage |
| Read messages from "Eli" | ListChats → find chat → ListChatMessages | `messages get` (instant, local) |
| Resolve unknown user | ListChats + filter → scan members | `lookup user` → single search call on miss |

The cache eliminates the expensive `ListChats` call (2000+ results) from every operation.

## Reference Files

Load these only when needed — do not read on every activation.

| File | When to load |
|------|-------------|
| `references/cache-format.md` | Debugging the SQLite schema or writing direct queries |
| `references/background-agents.md` | Orchestrating parallel or background cache operations |
| `references/html-cleanup.md` | Processing channel messages with HTML bodies |
| `references/writing-style.md` | Drafting or sending any message on behalf of the user |
