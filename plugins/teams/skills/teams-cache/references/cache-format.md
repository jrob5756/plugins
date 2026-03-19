# Teams Cache File Format Reference

## `me.json` — Current User

```json
{
  "displayName": "Jason Robert",
  "upn": "jasonrobert@microsoft.com",
  "userId": "2d969639-1bef-40b7-b9bf-d2de5419d32b",
  "timezone": "Eastern Standard Time"
}
```

## `users.json` — Known Users

Map of display name → user details. Keys are display names for easy lookup.

```json
{
  "Jason Robert": {
    "upn": "jasonrobert@microsoft.com",
    "userId": "2d969639-1bef-40b7-b9bf-d2de5419d32b"
  },
  "Lucio Cunha Tinoco": {
    "upn": "Lucio.Tinoco@microsoft.com",
    "userId": "0e23abe9-4e20-49eb-856c-671eb6c9cb93"
  }
}
```

## `chats.json` — Known Chats

Map of human-readable label → chat details. Labels are the display name (1:1), topic (group), or "Team > Channel" (channel).

```json
{
  "Lucio Cunha Tinoco": {
    "chatId": "19:0e23abe9..._2d969639...@unq.gbl.spaces",
    "type": "oneOnOne",
    "members": ["Jason Robert", "Lucio Cunha Tinoco"]
  },
  "Log Service Core Squad": {
    "chatId": "19:7a9b2046...@thread.v2",
    "type": "group",
    "members": ["Jason Robert", "..."]
  },
  "Azure Core CTO > General": {
    "chatId": "19:NMAnGh4e...@thread.tacv2",
    "type": "channel",
    "team": "Azure Core CTO",
    "teamId": "010f8f80-a082-4e06-9fe0-665a9748558d"
  }
}
```

### Chat types

| Type | Format | Example |
|------|--------|---------|
| `oneOnOne` | Display name of the other person | `"Eli Cortez"` |
| `group` | Topic of the group chat | `"Log Service Core Squad"` |
| `channel` | `"Team Name > Channel Name"` | `"SoftwareEE > AI Tools - SIG"` |

## `teams.json` — Known Teams

Map of team display name → team details with channels.

```json
{
  "Azure Core CTO": {
    "teamId": "010f8f80-a082-4e06-9fe0-665a9748558d",
    "channels": [
      {
        "name": "General",
        "channelId": "19:NMAnGh4e...@thread.tacv2"
      }
    ]
  }
}
```

## `messages/{safe-chat-id}.json` — Cached Messages

The `safe-chat-id` is the chat ID with `:`, `@`, `.`, and `/` replaced by `_`.

```json
{
  "chatId": "19:abc...@thread.v2",
  "label": "Log Service Core Squad",
  "lastFetched": "2026-03-19T14:00:00Z",
  "messages": [
    {
      "id": "1234567890",
      "sender": "Lucio Cunha Tinoco",
      "content": "Let's discuss the new architecture",
      "timestamp": "2026-03-19T13:45:00Z"
    }
  ]
}
```

### Message staleness

- **< 15 minutes** — Use cached messages
- **15–60 minutes** — Use cached but note they may be stale
- **> 60 minutes** — Fetch fresh messages

## Lookup Algorithms

### Name matching (case-insensitive, partial)

```python
def find_user(name, users_cache):
    name_lower = name.lower()
    # Exact match first
    for display_name, data in users_cache.items():
        if display_name.lower() == name_lower:
            return display_name, data
    # Partial match
    for display_name, data in users_cache.items():
        if name_lower in display_name.lower():
            return display_name, data
    return None, None
```

### Chat lookup by person name

```python
def find_chat(person_name, chats_cache):
    name_lower = person_name.lower()
    for label, data in chats_cache.items():
        if data.get('type') == 'oneOnOne' and name_lower in label.lower():
            return label, data
    return None, None
```
