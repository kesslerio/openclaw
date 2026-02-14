# Unified Inbox Feature Documentation

## Overview

The Unified Inbox is an Apple Mail-style three-column interface that aggregates messages from multiple platforms (WhatsApp, Telegram, Discord, Slack, Email) into a single view within the Kanban Mission Control application.

**Status**: Feature Complete, Ready for Production
**Last Updated**: 2026-02-05
**Port**: 8888 (same as Kanban Mission Control)

---

## Architecture

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Universal Briefing Database                   │
│              ~/.universal-briefing/briefing.db                   │
│                     (SQLite - messages table)                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend API (Express)                       │
│                    server/server.js:1454-1723                    │
│                                                                  │
│  Endpoints:                                                      │
│  • GET /api/messages        - List with filters                  │
│  • GET /api/messages/stats  - Platform statistics                │
│  • GET /api/messages/:p/:id - Single message detail              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (React)                             │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  useMessages │  │  Sidebar   │  │     App.jsx             │  │
│  │    Hook     │  │  (nav)     │  │  (routing + views)      │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│         │                                      │                 │
│         ▼                                      ▼                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    UnifiedInbox.jsx                          ││
│  │  ┌──────────────┬────────────────┬───────────────────────┐  ││
│  │  │ Platform     │ Message List   │ Message Detail        │  ││
│  │  │ Sidebar      │ (scrollable)   │ (full view)           │  ││
│  │  │ (filters)    │                │                       │  ││
│  │  └──────────────┴────────────────┴───────────────────────┘  ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## File Structure

### Backend

| File               | Lines     | Description            |
| ------------------ | --------- | ---------------------- |
| `server/server.js` | 1454-1723 | Messages API endpoints |

### Frontend

| File                                       | Description                         |
| ------------------------------------------ | ----------------------------------- |
| `frontend/src/components/UnifiedInbox.jsx` | Main component with 3-column layout |
| `frontend/src/components/Sidebar.jsx`      | Navigation with Inbox link          |
| `frontend/src/hooks/useMessages.js`        | Data fetching, polling, filtering   |
| `frontend/src/utils/api.js`                | API client functions                |
| `frontend/src/App.jsx`                     | Routing for inbox view              |

### Tests

| File                                                   | Tests | Description             |
| ------------------------------------------------------ | ----- | ----------------------- |
| `tests/unit/server/routes/messages.test.js`            | 91    | Backend API tests       |
| `tests/unit/frontend/hooks/useMessages.test.jsx`       | 42    | Hook tests              |
| `tests/unit/frontend/components/UnifiedInbox.test.jsx` | 85    | Component tests         |
| `tests/helpers/factories.ts`                           | -     | Message factories added |
| `tests/helpers/message-factory.js`                     | -     | Standalone factory      |

---

## API Reference

### GET /api/messages

Retrieves messages with optional filtering.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `platform` | string | `all` | Filter by platform (whatsapp, telegram, discord, slack, email, all) |
| `hours` | number | `24` | Messages from last N hours |
| `limit` | number | `100` | Max messages (capped at 1000) |
| `q` | string | - | Search in content and sender_name |

**Response:**

```json
{
  "messages": [
    {
      "id": "msg-123",
      "platform": "whatsapp",
      "sender_id": "1234567890@c.us",
      "sender_name": "1234567890@c.us",
      "displayName": "John Doe",
      "channel_name": null,
      "content": "Message text",
      "timestamp": "2026-02-05T12:00:00Z",
      "is_mention": false,
      "has_attachment": false
    }
  ],
  "platforms": { "whatsapp": 100, "telegram": 50 },
  "total": 150,
  "filters": { "platform": "all", "hours": 24, "limit": 100 },
  "timestamp": "2026-02-05T12:00:00Z"
}
```

### GET /api/messages/stats

Returns platform statistics.

**Response:**

```json
{
  "platforms": {
    "whatsapp": { "total": 444, "today": 214 },
    "telegram": { "total": 10, "today": 2 },
    "email": { "total": 99, "today": 0 }
  },
  "totalToday": 216,
  "totalAll": 553,
  "hourlyActivity": [{ "hour": "2026-02-05 14:00", "count": 30 }],
  "timestamp": "2026-02-05T12:00:00Z"
}
```

### GET /api/messages/:platform/:id

Returns a single message with parsed raw_data.

**Response:**

```json
{
  "id": "msg-123",
  "platform": "whatsapp",
  "displayName": "John Doe",
  "raw_data_parsed": { "_data": { "notifyName": "John Doe" } },
  ...
}
```

---

## Key Features

### 1. Auto-Loading

- Messages load automatically on mount
- No manual "Load" button required
- Polls every 30 seconds for updates

### 2. Platform Filtering

- Sidebar shows all platforms with counts
- Click to filter by platform
- "All Messages" shows everything

### 3. Search

- Real-time search across content and sender names
- Debounced (300ms) to prevent excessive API calls

### 4. Keyboard Navigation

- `j` / `↓` - Next message
- `k` / `↑` - Previous message
- Auto-selects first message on load

### 5. Display Name Extraction

- Extracts WhatsApp `notifyName` from nested `raw_data._data.notifyName`
- Falls back to `sender_name` then `sender_id`

### 6. Visual Indicators

- Platform-colored badges (green=WhatsApp, blue=Telegram, etc.)
- Attachment indicator (paperclip icon)
- @mention indicator
- Relative timestamps ("5m ago", "2h ago")

---

## Database Schema

The inbox reads from the Universal Briefing SQLite database:

**Location:** `~/.universal-briefing/briefing.db`

**Table:** `messages`

| Column           | Type    | Description                               |
| ---------------- | ------- | ----------------------------------------- |
| `id`             | TEXT    | Unique message ID                         |
| `platform`       | TEXT    | whatsapp, telegram, discord, slack, email |
| `sender_id`      | TEXT    | Platform-specific sender identifier       |
| `sender_name`    | TEXT    | Display name (may be ID for WhatsApp)     |
| `channel_name`   | TEXT    | Channel/group name (nullable)             |
| `content`        | TEXT    | Message text                              |
| `timestamp`      | TEXT    | ISO 8601 timestamp                        |
| `is_mention`     | INTEGER | 0 or 1                                    |
| `has_attachment` | INTEGER | 0 or 1                                    |
| `raw_data`       | TEXT    | JSON blob with platform-specific data     |

---

## Running the Application

```bash
# Start the server (includes inbox)
cd tools/kanban
node server/server.js

# Access the inbox
open http://localhost:8888
# Click "Inbox" in the sidebar
```

---

## Running Tests

```bash
cd tools/kanban/tests

# Run all Unified Inbox tests
npm test -- --run unit/server/routes/messages.test.js unit/frontend/hooks/useMessages.test.jsx unit/frontend/components/UnifiedInbox.test.jsx

# Run individual test suites
npm test -- --run unit/server/routes/messages.test.js      # 91 tests
npm test -- --run unit/frontend/hooks/useMessages.test.jsx  # 42 tests
npm test -- --run unit/frontend/components/UnifiedInbox.test.jsx  # 85 tests
```

---

## Dependencies

### Backend

- `better-sqlite3` - Synchronous SQLite access (already in server)
- `express` - HTTP server (existing)

### Frontend

- `react` - UI framework (existing)
- `lucide-react` - Icons (existing)

**No new dependencies were added.**

---

## Known Limitations

1. **Read-only**: Messages cannot be replied to or deleted from this interface
2. **No real-time updates**: Uses 30-second polling, not WebSocket
3. **Database dependency**: Requires Universal Briefing to be configured and running
4. **Single database**: Cannot aggregate from multiple briefing databases

---

## Future Enhancements

- [ ] WebSocket for real-time updates
- [ ] Reply functionality per platform
- [ ] Message actions (mark read, archive, delete)
- [ ] Conversation threading
- [ ] Platform-specific rich content (images, files)
- [ ] Notification badges for unread counts

---

## Changelog

### 2026-02-05

- Initial implementation of Unified Inbox
- Added Messages API endpoints to server.js
- Created UnifiedInbox component with 3-column layout
- Added useMessages hook with auto-fetch and polling
- Implemented platform filtering and search
- Added keyboard navigation (j/k, arrows)
- Fixed WhatsApp displayName extraction from nested raw_data
- Created comprehensive test suite (218 tests)
