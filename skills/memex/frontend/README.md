# 🎨 Memex Frontend - React UI

**Conversational interface to your personal memory**

Built with React 18 + Vite + TailwindCSS

---

## Features

### 1. Chat Interface 💬

- Conversational AI queries to your memory
- Real-time typing indicators
- Source attribution with confidence scores
- Message history with timestamps
- Clear conversation option

### 2. Journal View 📖

- Browse daily AI-generated journals
- Calendar navigation
- Mini-calendar with journal indicators
- Markdown rendering with Mermaid diagrams
- Date picker for quick navigation

### 3. Vector Search 🔍

- Semantic search across all transcripts
- Relevance + recency ranking
- Rich result cards with metadata
- Full-text preview
- Topic highlighting

---

## Quick Start

### Installation

```bash
cd /home/ubuntu/clawd/memex/frontend
npm install
```

### Development

```bash
npm run dev
# Opens at http://localhost:3000
```

### Build for Production

```bash
npm run build
# Output in dist/
```

### Preview Production Build

```bash
npm run preview
```

---

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Header.jsx          # Top navigation bar
│   │   ├── Sidebar.jsx         # Left sidebar navigation
│   │   ├── ChatInterface.jsx   # Conversational chat UI
│   │   ├── Message.jsx         # Chat message component
│   │   ├── JournalView.jsx     # Daily journal browser
│   │   └── SearchBar.jsx       # Vector search interface
│   ├── store/
│   │   └── useMemexStore.js    # Zustand state management
│   ├── App.jsx                 # Main app component
│   ├── main.jsx                # React entry point
│   └── index.css               # Global styles (TailwindCSS)
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
├── index.html
└── README.md (this file)
```

---

## State Management

Uses **Zustand** for lightweight state management:

```javascript
import useMemexStore from './store/useMemexStore'

function Component() {
  const { messages, sendMessage, isTyping } = useMemexStore()

  // Send a query
  await sendMessage("What did I discuss yesterday?")

  // Load journals
  await loadJournals('2026-01-01', '2026-01-31')

  // Perform search
  await performSearch("project updates")
}
```

---

## API Endpoints

The frontend expects these endpoints from the backend API:

### Chat

**POST /api/chat/query**

```json
{
  "query": "What did I promise Mark?"
}
```

Response:

```json
{
  "query": "What did I promise Mark?",
  "answer": "You promised to send the demo by Friday...",
  "sources": [
    {
      "date": "2026-01-28",
      "snippet": "In the meeting with Mark, I said...",
      "score": 0.92,
      "transcript_path": "transcripts/2026-01-28.txt"
    }
  ],
  "confidence": 0.85,
  "reasoning": "Synthesized from 3 sources"
}
```

### Journals

**GET /api/journals?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD**

Response:

```json
{
  "journals": [
    {
      "date": "2026-01-28",
      "content": "# Daily Journal - January 28, 2026\n\n## Summary\n...",
      "action_items": ["Send demo to Mark by Friday", "Follow up with Darwin on partnership"],
      "transcript_count": 5,
      "generated_at": "2026-01-29T08:00:00Z"
    }
  ]
}
```

### Search

**POST /api/search**

```json
{
  "query": "project updates",
  "limit": 10
}
```

Response:

```json
{
  "results": [
    {
      "text": "We discussed the project roadmap...",
      "metadata": {
        "date": "2026-01-28",
        "speaker": "Arvind",
        "source_file": "transcripts/2026-01-28.txt",
        "topics": ["project", "roadmap", "timeline"]
      },
      "score": 0.87,
      "final_score": 0.91
    }
  ]
}
```

---

## Environment Variables

Create `.env` file:

```bash
# Backend API URL
VITE_API_URL=http://localhost:8765

# Optional: Analytics
VITE_ANALYTICS_ID=your-analytics-id
```

---

## Styling

### Color Palette

```css
--memex-primary: #4f46e5 /* Indigo */ --memex-secondary: #06b6d4 /* Cyan */ --memex-accent: #f59e0b
  /* Amber */ --memex-bg: #0f172a /* Dark slate */ --memex-surface: #1e293b /* Slate 800 */
  --memex-text: #f1f5f9 /* Slate 100 */;
```

### Typography

- **Sans:** Inter (primary)
- **Mono:** Fira Code (code blocks)

### Component Classes

```css
.btn-primary    /* Primary action button */
.btn-secondary  /* Secondary button */
.input          /* Text input field */
.card           /* Content card */
.message-user   /* User chat bubble */
.message-assistant /* AI chat bubble */
```

---

## Components

### ChatInterface

Conversational query interface with:

- Message list with auto-scroll
- Input box with keyboard shortcuts
- Example queries for new users
- Clear conversation option
- Typing indicators

**Props:** None (uses global state)

### JournalView

Daily journal browser with:

- Calendar navigation
- Mini-calendar with indicators
- Date picker
- Markdown rendering
- Action item highlighting

**Props:** None (uses global state)

### SearchBar

Vector search interface with:

- Semantic search input
- Loading states
- Result cards
- Relevance scores
- Example queries

**Props:** None (uses global state)

### Message

Individual chat message with:

- User/assistant styling
- Markdown rendering
- Source cards
- Confidence badges
- Timestamps

**Props:**

- `message`: Message object

### Header

Top navigation bar with:

- Sidebar toggle
- Current view title
- Connection status
- Logo

**Props:**

- `sidebarOpen`: boolean
- `onToggleSidebar`: function
- `activeView`: string

### Sidebar

Left navigation with:

- View switching
- Message/journal counts
- Settings button
- Help button

**Props:**

- `activeView`: string
- `onViewChange`: function
- `onClose`: function

---

## Keyboard Shortcuts

### Chat

- **Enter** - Send message
- **Shift+Enter** - New line in message

### Navigation

- **Cmd/Ctrl + K** - Focus search (planned)
- **Cmd/Ctrl + J** - Open journals (planned)

---

## Responsive Design

- **Mobile** (< 640px): Stack layout, collapsible sidebar
- **Tablet** (640-1024px): Side-by-side, condensed sidebar
- **Desktop** (> 1024px): Full layout with wide sidebar

---

## Performance

### Optimizations

- Lazy loading for journal content
- Virtual scrolling for long message lists (planned)
- Debounced search input
- Memoized components
- Code splitting by route

### Bundle Size

- React 18: ~42 KB
- TailwindCSS (purged): ~8 KB
- Total: < 100 KB gzipped

---

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Production
vercel --prod
```

### Manual Build + Host

```bash
npm run build
# Upload dist/ to static host
```

### Docker

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile Safari 14+
- Chrome Android 90+

**Not supported:** IE11, Opera Mini

---

## Accessibility

- Semantic HTML
- ARIA labels on interactive elements
- Keyboard navigation
- Focus visible styles
- Screen reader friendly

---

## Testing

### Unit Tests (Planned)

```bash
npm test
```

### E2E Tests (Planned)

```bash
npm run test:e2e
```

---

## Development Tips

### Hot Module Replacement

Vite provides instant HMR. Changes reflect immediately without full reload.

### Debugging

Open React DevTools:

- Chrome/Firefox: Install React DevTools extension
- View component tree and state

### API Mocking

For development without backend:

```javascript
// src/store/useMemexStore.js
const MOCK_MODE = import.meta.env.DEV;

if (MOCK_MODE) {
  // Return mock data
  return mockData;
}
```

---

## Roadmap

### v0.2.0 (Planned)

- [ ] Mermaid diagram rendering in journals
- [ ] Full transcript viewer
- [ ] Export chat history
- [ ] Dark/light theme toggle

### v0.3.0 (Planned)

- [ ] Voice input for queries
- [ ] Streaming responses (WebSocket)
- [ ] Saved searches
- [ ] Custom date range filters

### v0.4.0 (Planned)

- [ ] Multi-user support
- [ ] Sharing journals
- [ ] Mobile app (React Native)

---

## Troubleshooting

### Build Fails

```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install
```

### API Connection Issues

Check:

1. Backend is running (`http://localhost:8765`)
2. CORS is enabled on backend
3. `.env` has correct `VITE_API_URL`

### Styling Issues

```bash
# Rebuild Tailwind
npm run build
```

---

## Contributing

### Code Style

- Use functional components
- Use hooks (no class components)
- TailwindCSS for styling (no inline styles)
- Zustand for state (no Redux/Context)

### Commit Messages

```
feat: Add journal export functionality
fix: Fix message scroll bug
docs: Update README with deployment steps
style: Format code with Prettier
```

---

## License

MIT (same as Memex project)

---

## Credits

**Built by:** Nike 🐾  
**For:** Arvind's Memex  
**Date:** 2026-02-02

**Stack:**

- React 18.3
- Vite 5.1
- TailwindCSS 3.4
- Zustand 4.5
- React Markdown 9.0
- Lucide React (icons)
- date-fns (date utilities)

---

🚀 **Ready to interact with your memory!**
