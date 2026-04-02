# HTML Cleanup for Teams Messages

## Why Cleanup Is Needed

Teams channel messages always return HTML bodies, even for simple text content. A plain "Hello" message arrives wrapped in `<p>Hello</p>`. Richer messages include `<h2>`, `<li>`, `<codeblock>`, and inline styles that are unreadable in a terminal.

**Rule: ALWAYS clean HTML before presenting channel message content to the user.**

Chat messages (1:1 and group) may also contain HTML, especially if the sender used formatting.

## CLI Command

```bash
python3 $TEAMS_CACHE util clean-html --stdin
```

Reads HTML from stdin, writes cleaned plaintext to stdout.

## Usage Examples

### Pipe a single message

```bash
echo '<p>Hello <b>team</b></p><p>Meeting at 3pm</p>' | python3 $TEAMS_CACHE util clean-html --stdin
# Output:
# Hello team
# Meeting at 3pm
```

### Clean a stored raw_html value

```bash
sqlite3 ~/.local/share/teams-mcp-cache/teams-cache.db \
  "SELECT raw_html FROM messages WHERE source_label='Azure Core CTO > General' AND id='123'" \
  | python3 $TEAMS_CACHE util clean-html --stdin
```

### In an agent workflow

```
1. Fetch channel messages via ListChannelMessages
2. For each message with HTML body:
   echo "$html_body" | python3 $TEAMS_CACHE util clean-html --stdin
3. Present the cleaned output to the user
```

## Cleanup Rules

The cleaner applies these transformations in order:

| HTML Pattern | Replacement | Example |
|-------------|-------------|---------|
| `<br />` or `<br/>` | Newline | `line1<br />line2` → `line1\nline2` |
| `<li>` | `- ` prefix | `<li>Item</li>` → `- Item\n` |
| `</li>` | Newline | (paired with above) |
| `<h1>`, `<h2>` | `\n## ` | `<h2>Title</h2>` → `\n## Title\n` |
| `</h1>`, `</h2>` | Newline | (paired with above) |
| `<h3>`, `<h4>` | `\n### ` | `<h3>Section</h3>` → `\n### Section\n` |
| `</h3>`, `</h4>` | Newline | (paired with above) |
| `<codeblock><code>` | `` \n``` \n `` | Code block open |
| `</code></codeblock>` | `` \n``` \n `` | Code block close |
| `<p>` | Strip (remove) | `<p>Text</p>` → `Text\n` |
| `</p>` | Newline | (paired with above) |
| All remaining tags | Strip | `<span style="...">text</span>` → `text` |
| HTML entities | Unescape | `&amp;` → `&`, `&lt;` → `<` |
| 3+ consecutive newlines | Collapse to 2 | Prevents excessive whitespace |

### Processing Order

1. `<br>` tags → newlines
2. `<li>` tags → list items
3. `<h1>`–`<h4>` → markdown headers
4. `<codeblock><code>` → fenced code blocks
5. `<p>` tags → paragraphs
6. Strip all remaining HTML tags
7. Unescape HTML entities
8. Collapse excessive newlines

## Before / After Example

**Raw HTML from Teams API:**

```html
<h2>Sprint Update</h2><p>Key changes this week:</p><li>Migrated auth to Entra ID</li><li>Fixed caching bug in ingestion pipeline</li><p>Code sample:</p><codeblock><code>def process(batch):
    return [transform(x) for x in batch]</code></codeblock><p>Questions? Ping me on Teams.</p>
```

**After cleanup:**

```
## Sprint Update
Key changes this week:
- Migrated auth to Entra ID
- Fixed caching bug in ingestion pipeline

Code sample:

```
def process(batch):
    return [transform(x) for x in batch]
```

Questions? Ping me on Teams.
```

## Fallback: Inline Python

If `$TEAMS_CACHE` is unavailable (e.g., script not found), use this Python heredoc:

```bash
python3 << 'PYEOF'
import sys, re, html

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

print(clean_html(sys.stdin.read()))
PYEOF
```

**Key rules for the fallback:**

- Always use a heredoc (`<< 'PYEOF'`) — inline `python3 -c` breaks on complex regexes
- Single-quote the delimiter (`'PYEOF'`) to prevent shell expansion
- Pipe the HTML into stdin: `echo "$html" | python3 << 'PYEOF' ...`

## When to Clean

| Message Source | Clean HTML? | Reason |
|---------------|-------------|--------|
| Channel messages (`ListChannelMessages`) | **Always** | Always HTML |
| Channel message replies (`ReplyToChannelMessage` response) | **Always** | Always HTML |
| Group chat messages | Check `contentType` | May be HTML or text |
| 1:1 chat messages | Check `contentType` | Usually text, sometimes HTML |
| Cached messages (`messages.content`) | **No** | Already cleaned on store |
| Cached raw HTML (`messages.raw_html`) | **Yes** | Stored for re-processing |
