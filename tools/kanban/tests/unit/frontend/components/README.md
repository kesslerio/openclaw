# UnifiedInbox Component Test Suite

## Overview

Comprehensive test suite for the UnifiedInbox component and its sub-components (PlatformSidebar, MessageItem, MessageDetail).

## Test File

- **Location**: `tests/unit/frontend/components/UnifiedInbox.test.jsx`
- **Framework**: Vitest + React Testing Library
- **Coverage**: 100+ test cases across all components

## Running Tests

### From tests directory:

```bash
npm test unit/frontend/components/UnifiedInbox.test.jsx
```

### Watch mode:

```bash
npm run test:watch unit/frontend/components/UnifiedInbox.test.jsx
```

### With coverage:

```bash
npm run test:coverage -- unit/frontend/components/UnifiedInbox.test.jsx
```

## Test Coverage

### 1. UnifiedInbox Component (Main)

#### Layout and Basic Rendering

- ✓ Renders three-column layout (sidebar, list, detail)
- ✓ Renders platform sidebar with all options
- ✓ Renders message list
- ✓ Renders search input
- ✓ Renders refresh button
- ✓ Renders message count

#### Loading State

- ✓ Shows loading skeleton when loading
- ✓ Shows skeleton in message list
- ✓ Shows skeleton in detail panel
- ✓ Hides loading skeleton when data loads

#### Error State

- ✓ Shows error message when error occurs
- ✓ Still shows messages when error present
- ✓ Styles error message correctly (red background)

#### Empty State

- ✓ Shows "No messages found" when empty
- ✓ Shows search hint when empty with search query
- ✓ No hint shown when empty without search

#### Message Selection

- ✓ Auto-selects first message on load
- ✓ Shows message detail when selected
- ✓ Updates detail panel when different message clicked
- ✓ Highlights selected message

#### Keyboard Navigation

- ✓ Moves to next message on 'j' key
- ✓ Moves to next message on ArrowDown
- ✓ Moves to previous message on 'k' key
- ✓ Moves to previous message on ArrowUp
- ✓ Prevents moving beyond first message
- ✓ Prevents moving beyond last message
- ✓ Does not interfere with search input typing

#### Search Functionality

- ✓ Calls setSearchQuery when typing
- ✓ Displays current search query in input
- ✓ Updates search query on change

#### Refresh Functionality

- ✓ Calls refresh when button clicked
- ✓ Disables button when loading
- ✓ Shows "Refreshing..." text when loading
- ✓ Animates refresh icon when loading

### 2. PlatformSidebar Component

#### Platform Options

- ✓ Renders all platform options (All, WhatsApp, Telegram, Discord, Slack, Email)
- ✓ Shows correct count for each platform from stats
- ✓ Shows counts for: All (150), WhatsApp (45), Telegram (32), Discord (28), Slack (25), Email (20)

#### Platform Selection

- ✓ Highlights active platform
- ✓ Highlights "All Messages" when platform is "all"
- ✓ Calls setPlatform when platform clicked
- ✓ Calls setPlatform with correct platform ID

#### Platform Icons

- ✓ Shows proper icon for each platform

#### Stats Handling

- ✓ Shows 0 when stats are null
- ✓ Shows 0 for missing platform stats

### 3. MessageItem Component

#### Message Content

- ✓ Renders sender name from displayName
- ✓ Fallback to sender_name when displayName missing
- ✓ Shows platform badge with platform name
- ✓ Shows platform badge with correct color (green for WhatsApp, blue for Telegram)
- ✓ Shows message timestamp (relative format)
- ✓ Truncates long content with ellipsis (max 100 chars)
- ✓ Does not truncate short content

#### Message Indicators

- ✓ Shows attachment indicator (paperclip icon) when has_attachment=true
- ✓ Hides attachment indicator when has_attachment=false
- ✓ Shows @mention indicator when is_mention=true
- ✓ Hides @mention indicator when is_mention=false

#### Selection State

- ✓ Shows selected state styling (blue background)
- ✓ Only one message shows selected state

#### Click Handling

- ✓ Messages are clickable buttons
- ✓ Changes selection when clicked
- ✓ Updates detail panel on click

### 4. MessageDetail Component

#### Message Selection

- ✓ Shows "Select a message to view details" when no message selected
- ✓ Renders full message when message provided

#### Sender Information

- ✓ Shows sender name from displayName (or sender_name fallback)
- ✓ Shows sender avatar with initial letter
- ✓ Shows sender_id in details section

#### Platform Information

- ✓ Shows platform badge
- ✓ Shows channel_name when present
- ✓ Hides channel section when channel_name missing

#### Timestamp Display

- ✓ Shows full timestamp (localized date/time)
- ✓ Shows relative time (e.g., "2h ago")

#### Message Content

- ✓ Shows full content (not truncated)
- ✓ Preserves whitespace (whitespace-pre-wrap class)

#### Message Metadata

- ✓ Shows "Attachments present" when has_attachment=true
- ✓ Hides attachment text when has_attachment=false
- ✓ Shows "@mentioned" when is_mention=true
- ✓ Hides mention text when is_mention=false

#### Message Details Section

- ✓ Shows "Message Details" heading
- ✓ Shows "Sender ID:" label and value

### 5. Helper Functions

#### formatRelativeTime

- ✓ Returns "Just now" for timestamps < 60 seconds
- ✓ Returns "Xm ago" for timestamps in minutes
- ✓ Returns "Xh ago" for timestamps in hours
- ✓ Returns "Xd ago" for timestamps in days

#### getAvatarColor

- ✓ Returns consistent color for same name
- ✓ Uses hash-based color selection from palette

## Mock Setup

### useMessages Hook Mock

The test suite mocks the `useMessages` hook with configurable return values:

```javascript
const mockUseMessages = vi.fn();
vi.mock("../../../../frontend/src/hooks/useMessages", () => ({
  useMessages: () => mockUseMessages(),
}));

// Default mock return
const defaultHookReturn = {
  messages: mockMessages,
  stats: mockStats,
  loading: false,
  error: null,
  platform: "all",
  setPlatform: vi.fn(),
  searchQuery: "",
  setSearchQuery: vi.fn(),
  refresh: vi.fn(),
};
```

### Icon Mocks

All lucide-react icons are mocked to prevent rendering issues:

```javascript
vi.mock("lucide-react", () => ({
  Search: () => <svg data-testid="search-icon" />,
  RefreshCw: ({ className }) => <svg data-testid="refresh-icon" className={className} />,
  // ... other icons
}));
```

## Sample Test Data

### Mock Messages

```javascript
const mockMessages = [
  {
    id: "msg-1",
    displayName: "John Doe",
    sender_name: "John Doe",
    sender_id: "user-123",
    platform: "whatsapp",
    content: "Hello, this is a test message",
    timestamp: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
    has_attachment: false,
    is_mention: false,
  },
  // ... more messages
];
```

### Mock Stats

```javascript
const mockStats = {
  totalAll: 150,
  platforms: {
    whatsapp: { total: 45 },
    telegram: { total: 32 },
    discord: { total: 28 },
    slack: { total: 25 },
    email: { total: 20 },
  },
};
```

## Test Patterns

### Testing Component Rendering

```javascript
it("should render sender name from displayName", () => {
  render(<UnifiedInbox />);
  expect(screen.getByText("John Doe")).toBeDefined();
});
```

### Testing User Interactions

```javascript
it("should call setPlatform when platform is clicked", () => {
  const setPlatform = vi.fn();
  mockUseMessages.mockReturnValue({
    ...defaultHookReturn,
    setPlatform,
  });

  render(<UnifiedInbox />);

  const telegramButton = screen.getByText("Telegram").closest("button");
  fireEvent.click(telegramButton);

  expect(setPlatform).toHaveBeenCalledWith("telegram");
});
```

### Testing Keyboard Events

```javascript
it("should move to next message on j key", async () => {
  render(<UnifiedInbox />);

  fireEvent.keyDown(window, { key: "j" });

  await waitFor(() => {
    expect(screen.getByText("Second message content")).toBeDefined();
  });
});
```

### Testing Conditional Rendering

```javascript
it("should show error message when error occurs", () => {
  mockUseMessages.mockReturnValue({
    ...defaultHookReturn,
    error: "Failed to load messages",
  });

  render(<UnifiedInbox />);

  expect(screen.getByText("Failed to load messages")).toBeDefined();
});
```

## Coverage Goals

- **Lines**: 95%+
- **Branches**: 90%+
- **Functions**: 95%+
- **Statements**: 95%+

## Dependencies

Required for tests to run:

- `vitest` - Test framework
- `@testing-library/react` - React testing utilities
- `@testing-library/jest-dom` - DOM matchers
- `jsdom` - DOM environment (must be installed in tests directory)
- `@vitejs/plugin-react` - React plugin for Vite
- `react` and `react-dom` - React dependencies

## Notes

1. **jsdom Environment**: Tests require jsdom to simulate browser DOM. The vitest config specifies `environment: 'jsdom'` for frontend tests.

2. **Hook Mocking**: The `useMessages` hook is mocked at the module level, allowing each test to customize the return values as needed.

3. **Icon Mocking**: All lucide-react icons are mocked to prevent rendering issues and simplify test assertions.

4. **Keyboard Navigation**: Keyboard event tests use `fireEvent.keyDown(window, { key: 'j' })` to simulate global keyboard shortcuts.

5. **Auto-selection**: The component auto-selects the first message on mount, which is tested across multiple scenarios.

6. **Relative Time**: Helper function tests validate time formatting for different time ranges (seconds, minutes, hours, days).

## Troubleshooting

### Missing jsdom

If you see `Cannot find dependency 'jsdom'`, install it in the tests directory:

```bash
npm install --save-dev jsdom
```

### React Hook Errors

If you see "Invalid hook call" errors, ensure the vitest config has proper React aliases to prevent dual React instances:

```javascript
resolve: {
  alias: {
    'react': path.resolve(__dirname, '../node_modules/react'),
    'react-dom': path.resolve(__dirname, '../node_modules/react-dom'),
  },
}
```

### Import Errors

Ensure the test file imports match the actual component file structure. The mock paths must exactly match the import paths used in the component.

## Future Enhancements

Potential test additions:

1. **Accessibility Tests**: Add jest-axe tests for WCAG compliance
2. **Performance Tests**: Add render performance benchmarks
3. **Visual Regression Tests**: Add screenshot testing
4. **Integration Tests**: Test with real API endpoints
5. **E2E Tests**: Test full user workflows with Playwright

## Related Files

- **Component**: `/Users/arvindsarin/Cursor/Claude-2026/openclaw/tools/kanban/frontend/src/components/UnifiedInbox.jsx`
- **Hook**: `/Users/arvindsarin/Cursor/Claude-2026/openclaw/tools/kanban/frontend/src/hooks/useMessages.js`
- **Test Utils**: `/Users/arvindsarin/Cursor/Claude-2026/openclaw/tools/kanban/tests/helpers/test-utils.tsx`
- **Vitest Config**: `/Users/arvindsarin/Cursor/Claude-2026/openclaw/tools/kanban/tests/config/vitest.config.ts`
