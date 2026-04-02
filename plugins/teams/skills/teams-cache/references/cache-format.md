# Teams Cache SQLite Schema Reference

## Database Location


```
~/.local/share/teams-mcp-cache/teams-cache.db
```
Created automatically by `teams_cache.py init`. All cache operations use this single SQLite file.

## Relationships

```
me (singleton)    users ◄── chat_members ──► chats ──► favorites
                  teams ──► channels                   messages ──► sync_meta
```

- `chat_members.display_name` → `users.display_name`
- `chat_members.chat_label` → `chats.label`
- `chats.team_name` → `teams.team_name` (channels only)
- `channels.team_name` → `teams.team_name`
- `messages.source_label` → `chats.label` / `favorites.label`
- `sync_meta.source_label` → `favorites.label`

## Tables

### `me` — Current User (singleton)

Stores the authenticated user's identity. Always exactly one row.

| Column       | Type | Description                          |
|-------------|------|--------------------------------------|
| display_name | TEXT | Full display name                    |
| upn          | TEXT | User Principal Name (email)          |
| user_id      | TEXT | Microsoft Graph GUID                 |
| timezone     | TEXT | IANA or Windows timezone identifier  |

```sql
INSERT INTO me VALUES ('Jason Robert', 'jasonrobert@microsoft.com',
  '2d969639-1bef-40b7-b9bf-d2de5419d32b', 'Eastern Standard Time');
```

### `users` — Known Users

| Column       | Type | Constraint  | Description               |
|-------------|------|-------------|---------------------------|
| display_name | TEXT | PRIMARY KEY | Full display name         |
| upn          | TEXT |             | User Principal Name       |
| user_id      | TEXT |             | Microsoft Graph GUID      |

```sql
-- Example data
INSERT INTO users VALUES ('Lucio Cunha Tinoco', 'lucio.tinoco@microsoft.com', '0e23abe9-4e20-49eb-856c-671eb6c9cb93');
INSERT INTO users VALUES ('Eli Cortez',         'elicortez@microsoft.com',    'a1b2c3d4-5678-9abc-def0-1234567890ab');
INSERT INTO users VALUES ('Nilton Saraiva',     'niltons@microsoft.com',      'b2c3d4e5-6789-abcd-ef01-234567890abc');
```

### `chats` — Known Chats

| Column    | Type | Constraint  | Description                                  |
|-----------|------|-------------|----------------------------------------------|
| label     | TEXT | PRIMARY KEY | Human-readable label (see label conventions) |
| chat_id   | TEXT |             | Teams thread ID (`19:...@thread.v2` etc.)    |
| type      | TEXT |             | `oneOnOne`, `group`, or `channel`            |
| team_name | TEXT |             | Parent team name (channels only, else NULL)  |
| team_id   | TEXT |             | Parent team GUID (channels only, else NULL)  |

**Label conventions:** oneOnOne → person name, group → topic, channel → `Team > Channel`.

```sql
INSERT INTO chats VALUES ('Eli Cortez',               '19:a1b2...@unq.gbl.spaces', 'oneOnOne', NULL,            NULL);
INSERT INTO chats VALUES ('Log Service Core Squad',    '19:7a9b...@thread.v2',      'group',    NULL,            NULL);
INSERT INTO chats VALUES ('Azure Core CTO > General',  '19:NMAn...@thread.tacv2',   'channel',  'Azure Core CTO','010f8f80-a082-4e06-9fe0-665a9748558d');
```

### `chat_members` — Chat Membership (many-to-many)

| Column       | Type | Description                            |
|-------------|------|----------------------------------------|
| chat_label   | TEXT | FK → `chats.label`                     |
| display_name | TEXT | Member's display name (matches `users`)|

Primary key: `(chat_label, display_name)`

```sql
INSERT INTO chat_members VALUES ('Log Service Core Squad', 'Jason Robert');
INSERT INTO chat_members VALUES ('Log Service Core Squad', 'Lucio Cunha Tinoco');
INSERT INTO chat_members VALUES ('Log Service Core Squad', 'Eli Cortez');
```

### `teams` — Known Teams

| Column    | Type | Constraint  | Description          |
|-----------|------|-------------|----------------------|
| team_name | TEXT | PRIMARY KEY | Team display name    |
| team_id   | TEXT |             | Microsoft Graph GUID |

```sql
INSERT INTO teams VALUES ('Azure Core CTO',  '010f8f80-a082-4e06-9fe0-665a9748558d');
INSERT INTO teams VALUES ('SoftwareEE',      'f1e2d3c4-b5a6-7890-1234-567890abcdef');
```

### `channels` — Team Channels

| Column       | Type | Description                              |
|-------------|------|------------------------------------------|
| team_name    | TEXT | FK → `teams.team_name`                   |
| channel_name | TEXT | Channel display name                     |
| channel_id   | TEXT | Teams channel thread ID (`@thread.tacv2`)|

Primary key: `(team_name, channel_name)`

```sql
INSERT INTO channels VALUES ('Azure Core CTO', 'General',           '19:NMAn...@thread.tacv2');
INSERT INTO channels VALUES ('SoftwareEE',     'AI Tools - SIG',    '19:xYz1...@thread.tacv2');
INSERT INTO channels VALUES ('SoftwareEE',     'General',           '19:aBcD...@thread.tacv2');
```

### `favorites` — Chats/Channels to Auto-Sync

| Column | Type | Constraint  | Description                       |
|--------|------|-------------|-----------------------------------|
| label  | TEXT | PRIMARY KEY | Matches `chats.label`             |
| type   | TEXT |             | `chat`, `group`, or `channel`     |

```sql
INSERT INTO favorites VALUES ('Log Service Core Squad',   'group');
INSERT INTO favorites VALUES ('Azure Core CTO > General', 'channel');
INSERT INTO favorites VALUES ('Eli Cortez',               'chat');
```

### `messages` — Cached Messages

| Column       | Type | Description                                   |
|-------------|------|-----------------------------------------------|
| source_label | TEXT | Chat/channel label (matches `chats.label`)    |
| id           | TEXT | Message ID from Teams API                     |
| sender       | TEXT | Sender's display name                         |
| content      | TEXT | Cleaned plaintext content                     |
| timestamp    | TEXT | ISO 8601 timestamp                            |
| raw_html     | TEXT | Original HTML body (NULL for plain-text chats)|

Primary key: `(source_label, id)`  
Index: `idx_messages_ts ON messages(source_label, timestamp DESC)`

```sql
INSERT INTO messages VALUES ('Log Service Core Squad', '1719432000123', 'Lucio Cunha Tinoco',
  'Let''s discuss the new architecture for the ingestion pipeline.', '2026-03-19T13:45:00Z', NULL);
INSERT INTO messages VALUES ('Azure Core CTO > General', '1719435600456', 'Eli Cortez',
  '## Sprint Review\n- Completed auth migration', '2026-03-19T14:00:00Z',
  '<h2>Sprint Review</h2><li>Completed auth migration</li>');
```

### `sync_meta` — Sync Timestamps

| Column        | Type    | Constraint  | Description                        |
|--------------|---------|-------------|------------------------------------|
| source_label  | TEXT    | PRIMARY KEY | Matches `favorites.label`          |
| last_fetched  | TEXT    |             | ISO 8601 timestamp of last sync    |
| message_count | INTEGER |             | Number of messages stored for this source |

```sql
INSERT INTO sync_meta VALUES ('Log Service Core Squad',   '2026-03-19T14:05:00Z', 47);
INSERT INTO sync_meta VALUES ('Azure Core CTO > General', '2026-03-19T13:30:00Z', 128);
```

## Common Agent Queries

```sql
-- Look up a user by partial name (case-insensitive)
SELECT * FROM users WHERE display_name LIKE '%lucio%' COLLATE NOCASE;

-- Find a 1:1 chat by person name
SELECT * FROM chats WHERE type = 'oneOnOne' AND label LIKE '%eli%' COLLATE NOCASE;

-- Find a channel by team and channel name
SELECT c.channel_id, ch.chat_id
FROM channels c
JOIN chats ch ON ch.label = c.team_name || ' > ' || c.channel_name
WHERE c.team_name LIKE '%core cto%' COLLATE NOCASE
  AND c.channel_name LIKE '%general%' COLLATE NOCASE;

-- Get recent messages from a chat/channel
SELECT sender, content, timestamp
FROM messages
WHERE source_label = 'Log Service Core Squad'
ORDER BY timestamp DESC LIMIT 20;

-- Find stale favorites (not synced in last 15 minutes)
SELECT f.label, f.type, sm.last_fetched
FROM favorites f
LEFT JOIN sync_meta sm ON f.label = sm.source_label
WHERE sm.last_fetched IS NULL
   OR sm.last_fetched < datetime('now', '-15 minutes');

-- Get all members of a group chat
SELECT display_name FROM chat_members WHERE chat_label = 'Log Service Core Squad';
-- Current user identity
SELECT * FROM me LIMIT 1;
```
