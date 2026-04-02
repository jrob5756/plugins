# Background Agent Patterns for Teams Cache

Patterns for using background agents to keep the Teams cache fresh without blocking the user's workflow.

## Script Path

The CLI tool lives at `plugins/teams/scripts/teams_cache.py` relative to workspace root.
The SKILL.md defines a `$TEAMS_CACHE` variable that agents should use. If unavailable:

```bash
TEAMS_CACHE="$(find ~ -path '*/plugins/teams/scripts/teams_cache.py' -maxdepth 6 2>/dev/null | head -1)"
```

---

## 1. Session-Start Sync

On session start, the plugin hook fires `teams-cache init` which ensures the DB exists and purges messages older than 7 days. After init, a background sync should refresh stale favorites.

### Agent Instruction Pattern

```
When invoked at session start:
1. Run `python3 $TEAMS_CACHE sync needed` to get stale favorites
2. For each stale favorite, launch a background agent to:
   a. Fetch latest messages via Teams MCP tools (ListChatMessages or ListChannelMessages)
   b. Pipe results to `python3 $TEAMS_CACHE messages store <label> --stdin`
3. Continue with the user's request — don't wait for sync to complete
```

### Example: Sync Stale Favorites

```bash
# Step 1 — identify what's stale (returns JSON list)
python3 $TEAMS_CACHE sync needed
# Output: [{"label": "Log Service Core Squad", "type": "group", "stale_minutes": 45},
#          {"label": "Azure Core CTO > General", "type": "channel", "stale_minutes": 120}]
```

For each entry, a background agent runs:

```
# For a group chat
Use ListChatMessages with chatId from cache for "Log Service Core Squad"
Pipe result JSON to: python3 $TEAMS_CACHE messages store "Log Service Core Squad" --stdin

# For a channel
Use ListChannelMessages with teamId + channelId from cache for "Azure Core CTO > General"
Pipe result JSON to: python3 $TEAMS_CACHE messages store "Azure Core CTO > General" --stdin
```

The main agent proceeds with the user's request immediately.

---

## 2. Parallel Lookups

When resolving multiple users or chats for a batch operation, launch parallel agents instead of sequential lookups.

### Example: "Send a message to Lucio, Eli, and Nilton"

```
1. Read users table — check which names are cached
2. For any cache misses, launch parallel explore agents:
   - Agent A: look up "Lucio" via ListChats + user search
   - Agent B: look up "Nilton" via ListChats + user search
3. Eli is cached → resolve immediately
4. Wait for parallel agents → update cache with new entries
5. Send messages sequentially (PostMessage for each)
```

### When to Parallelize

| Scenario | Sequential | Parallel |
|----------|-----------|----------|
| 1 unknown user | ✓ | — |
| 2+ unknown users | — | ✓ Launch one agent per user |
| 1 unknown chat + 1 unknown user | — | ✓ Independent lookups |
| Chain of dependent lookups | ✓ | — |

---

## 3. Non-Blocking Refresh

When cached data exists but is stale, return the cached version immediately and refresh in the background.

### Example: "Read my messages from Log Service Core Squad"

```
1. Check sync_meta: last_fetched = 25 minutes ago (stale but usable)
2. Read cached messages from messages table → present to user immediately
3. Note to user: "Showing cached messages from 25 min ago, refreshing..."
4. Launch background agent:
   a. Fetch fresh messages via ListChatMessages
   b. Run: python3 $TEAMS_CACHE messages store "Log Service Core Squad" --stdin
   c. Update sync_meta timestamp
5. If user asks again later, they get fresh data
```

### Staleness Thresholds

| Age | Action |
|-----|--------|
| < 15 min | Use cached, no refresh |
| 15–60 min | Use cached + background refresh |
| > 60 min | Fetch fresh (block), then cache |

---

## 4. Batch Message Send

When sending the same or similar message to multiple recipients, resolve all identifiers first, then send sequentially.

### Example: "Tell the core team that standup is moved to 3pm"

```
1. Identify recipients: read chat_members for "Log Service Core Squad"
   → Jason Robert, Lucio Cunha Tinoco, Eli Cortez, Nilton Saraiva
2. Exclude self (from me table)
3. Resolve chat IDs in parallel:
   - Check chats table for 1:1 chats with each person
   - Launch parallel agents for any cache misses
4. Send messages sequentially:
   - PostMessage to Lucio's chat: "Standup moved to 3pm"
   - PostMessage to Eli's chat: "Standup moved to 3pm"
   - PostMessage to Nilton's chat: "Standup moved to 3pm"
5. Cache any newly discovered chats
```

### Why Sequential Sends?

- Avoids Teams API rate limiting
- Ensures delivery confirmation per message
- Allows the agent to report progress ("Sent to Lucio ✓, Eli ✓, Nilton ✓")

---

## Background Agent Launch Checklist

Before launching a background agent for Teams cache operations:

1. **Provide full context** — background agents are stateless; include DB path, label, and IDs
2. **Include the script path** — pass `$TEAMS_CACHE` or the resolved absolute path
3. **Specify the cache update command** — the agent must know how to write results back
4. **Set a reasonable timeout** — Teams API calls rarely exceed 30 seconds
5. **Don't depend on the result** — if the background agent fails, cached data is still usable
