---
name: teams-cache
description: |
  Teams MCP efficiency layer with local caching of user UPNs, chat IDs, team IDs,
  channel IDs, and recent messages. ALWAYS use this skill for ANY operation involving
  Teams MCP tools — including sending messages, reading messages, listing chats,
  posting to channels, or looking up users. This skill MUST be activated before
  calling ANY Teams MCP tool (ListChats, PostMessage, ListChatMessages, ListTeams,
  ListChannels, PostChannelMessage, ListChannelMessages, SendMessageToSelf,
  SearchTeamsMessages, CreateChat, etc.). Triggers: send message, read message,
  message someone, chat with, reply to, latest message, post to channel, teams,
  send teams message, check teams, teams chat, read teams messages, post to teams,
  teams channel, teams lookup, find teams chat, teams user, who is on teams,
  list teams chats, teams group, teams meeting. Always invoke this skill first
  to check the local cache and avoid redundant API lookups.
---

# Teams Cache — Efficient Teams MCP Usage

Every Teams MCP operation requires identifiers (user UPNs, chat IDs, team IDs, channel IDs) that are expensive to look up via API. This skill provides a local cache layer that eliminates redundant lookups.

## Cache Location

```
~/.local/share/teams-mcp-cache/
├── me.json              # Current user identity
├── users.json           # Display name → UPN + userId mapping
├── chats.json           # Chat label → chatId + type + members
├── teams.json           # Team name → teamId + channels
└── messages/            # Recent messages per chat or channel
    └── {safe-id}.json   # safe-id: chat ID or channel ID with :@/ replaced by _
```

## Cache-First Workflow

**Before ANY Teams MCP tool call that requires an identifier:**

### Step 1: Read the cache

```bash
cat ~/.local/share/teams-mcp-cache/users.json   # For user lookups
cat ~/.local/share/teams-mcp-cache/chats.json    # For chat lookups
cat ~/.local/share/teams-mcp-cache/teams.json    # For team/channel lookups
```

### Step 2: Look up the identifier

Search by display name (case-insensitive, partial match OK):
- User name → get `upn` and `userId`
- Chat label → get `chatId`
- Team name → get `teamId`
- Channel name → get `channelId` from team's `channels` array

### Step 3: Use or fetch

- **Cache hit** → Use the cached identifier directly. Skip the API call entirely.
- **Cache miss** → Make the API call, then proceed to Step 4.

### Step 4: Update the cache (on miss only)

After any API call that returns new data, update the cache file:

```python
import json, os

def update_cache(filename, key, value):
    path = os.path.expanduser(f'~/.local/share/teams-mcp-cache/{filename}')
    with open(path) as f:
        cache = json.load(f)
    cache[key] = value
    with open(path, 'w') as f:
        json.dump(cache, f, indent=2)
```

## Identifier Lookup Patterns

### Finding a User UPN

```
1. Read ~/.local/share/teams-mcp-cache/users.json
2. Search for display name (case-insensitive substring match)
3. Found? → Return {upn, userId}
4. Not found? → Use the cache miss resolution steps below → Add to users.json
```

#### User cache miss resolution/

When a user is not in the cache, resolve their identity using these methods in priority order:

**Method 1: SearchTeamMessagesQueryParameters (preferred)**
Search for messages from the user — this returns their display name, email/UPN, and chatId in one call:
```
queryString: "from:FirstName LastName"
size: 3
```
Extract from the response:
- `from.emailAddress.name` → display name
- `from.emailAddress.address` → UPN (email)
- `chatId` → chat ID (also update chats.json)

This is the best method because it resolves the user, their UPN, AND the chat ID simultaneously.

**Method 2: SearchTeamsMessages (natural language fallback)**
If the name is ambiguous or Method 1 returns no results:
```
message: "messages from FirstName LastName"
```
Parse the response for user identity details and chat context.

**After resolving, always update BOTH caches:**
```python
# Add to users.json
users["Display Name"] = {"upn": "user@domain.com", "userId": "guid"}

# Add to chats.json (if a 1:1 chat was found)
chats["Display Name"] = {
    "chatId": "19:...@unq.gbl.spaces",
    "type": "oneOnOne",
    "members": ["Jason Robert", "Display Name"]
}
```

### Finding a Chat ID

```
1. Read ~/.local/share/teams-mcp-cache/chats.json
2. Search by label (person name for 1:1, topic for groups)
3. Found? → Return chatId
4. Not found? → First resolve the user UPN (see above), then call ListChats
   with user UPN filter → Add to chats.json
```

### Finding a Team / Channel ID

```
1. Read ~/.local/share/teams-mcp-cache/teams.json
2. Search by team name → get teamId
3. Search team's channels array by channel name → get channelId
4. Not found? → Call ListTeams / ListChannels → Add to teams.json
```

## Reading Channel Messages

Channel messages require special handling — they have a different response structure than chat messages and their bodies are always HTML.

### Channel message response structure

```
from.displayName   — sender name (flat, NOT nested under from.user)
from.id            — sender user ID
subject            — often empty; do NOT rely on this for matching
body.contentType   — always "Html"
body.content       — raw HTML; MUST be cleaned before presenting
createdDateTime    — ISO timestamp
```

### Finding a specific channel message

```
1. Read ~/.local/share/teams-mcp-cache/teams.json
2. Resolve teamId + channelId by name
3. Call ListChannelMessages with teamId + channelId
4. Match by from.displayName (sender), createdDateTime (date), or body content keywords
5. Clean HTML from body.content before presenting
6. Cache discovered messages and new users
```

### Reading thread replies

`ListChannelMessages` only returns **top-level posts**. To read threaded replies under a post, run the fetch-replies Python script defined in the agent instructions. The script:

1. Gets a Graph API token via `az account get-access-token`
2. Calls `GET /teams/{teamId}/channels/{channelId}/messages/{messageId}/replies`
3. Cleans HTML from each reply body
4. Prints formatted results

```
1. Read ~/.local/share/teams-mcp-cache/teams.json
2. Resolve teamId + channelId by name
3. Call ListChannelMessages to find the parent post (match by sender/date/keywords)
4. Run the fetch-replies Python heredoc with teamId, channelId, messageId
5. Clean HTML from reply bodies
6. Cache discovered users from reply senders
```

### HTML Cleanup (REQUIRED for channel messages)

Channel message bodies are raw HTML. Always clean before presenting.

Use a heredoc to avoid shell escaping issues:

```bash
python3 << 'PYEOF'
import json, html, re

def clean_html(raw):
    text = re.sub(r'<br\s*/?>', '\n', raw)
    text = re.sub(r'<li[^>]*>', '- ', text)
    text = re.sub(r'</li>', '\n', text)
    text = re.sub(r'<h[12][^>]*>', '\n## ', text)
    text = re.sub(r'</h[12]>', '\n', text)
    text = re.sub(r'<h[34][^>]*>', '\n### ', text)
    text = re.sub(r'</h[34]>', '\n', text)
    text = re.sub(r'<codeblock[^>]*><code>', '\n```\n', text)
    text = re.sub(r'</code></codeblock>', '\n```\n', text)
    text = re.sub(r'<p[^>]*>', '', text)
    text = re.sub(r'</p>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()
PYEOF
```

**Key rules:**
- Always use a heredoc (`<< 'PYEOF'`) — inline `python3 -c` breaks on complex regexes
- Strip HTML BEFORE presenting any channel message content
- Preserve code blocks, headers, and list structure when converting

## Message Caching

After reading messages from a chat or channel, cache them locally:

```
~/.local/share/teams-mcp-cache/messages/{safe-id}.json
```

Where `safe-id` replaces `:`, `@`, and `/` with `_`. Works for both chat IDs and channel IDs.

### Message cache format

```json
{
  "chatId": "19:abc...@thread.v2",
  "label": "Log Service Core Squad",
  "lastFetched": "2026-03-19T14:00:00Z",
  "messages": [
    {
      "id": "msg-id",
      "sender": "Display Name",
      "content": "Cleaned plaintext content",
      "timestamp": "2026-03-19T13:45:00Z"
    }
  ]
}
```

### When to use cached messages

- If `lastFetched` is within the last 15 minutes → use cached messages
- If older → fetch fresh messages and update cache
- Always fetch fresh for "latest" or "new" message requests

## Performance Impact

| Operation | Without Cache | With Cache |
|-----------|--------------|------------|
| Send message to "Lucio" | ListChats (2389 results) → find chat → PostMessage | Read users.json + chats.json → PostMessage |
| Post to "General" channel | ListTeams → ListChannels → PostChannelMessage | Read teams.json → PostChannelMessage |
| Read messages from "Eli" | ListChats → ListChatMessages | Read chats.json → ListChatMessages |

The cache eliminates the expensive `ListChats` call (which returns 2000+ results) for every single operation.

## Cache Maintenance

### Refreshing stale data

The cache is populated on first use and updated on cache misses. For a full refresh:

```bash
# Delete and rebuild (agent will repopulate on next use)
rm ~/.local/share/teams-mcp-cache/users.json
rm ~/.local/share/teams-mcp-cache/chats.json
rm ~/.local/share/teams-mcp-cache/teams.json
```

### Adding new contacts

When the agent discovers a new user through any API call, it should automatically add them to `users.json`. This includes users found in:
- Chat member lists
- Channel member lists
- Meeting participants
- Message senders

## Integration with Teams MCP Tools

This skill works with ALL Teams MCP tools:

| Tool | Cache benefit |
|------|--------------|
| `ListChats` | Cache result → never call again for same user |
| `PostMessage` | Cache provides chatId → skip ListChats |
| `ListChatMessages` | Cache provides chatId + message history |
| `ListTeams` | Cache provides teamId → skip for known teams |
| `ListChannels` | Cache provides channelId → skip for known channels |
| `PostChannelMessage` | Cache provides teamId + channelId |
| `ListChannelMessages` | Cache provides teamId + channelId; cache messages + new users from results |
| `ReplyToChannelMessage` | Cache provides teamId + channelId + messageId |
| `SearchTeamsMessages` | Cache new users/chats from results |
| `CreateChat` | Cache the new chat immediately |

## Current User

The current user's identity is cached in `me.json`:

```json
{
  "displayName": "Jason Robert",
  "upn": "jasonrobert@microsoft.com",
  "userId": "2d969639-1bef-40b7-b9bf-d2de5419d32b",
  "timezone": "Eastern Standard Time"
}
```

Use this for any self-referencing operations (e.g., "my chats", "send to myself").
