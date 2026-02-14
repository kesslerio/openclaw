# Drag-and-Drop Test Suite

Comprehensive test suite for Kanban board drag-and-drop functionality using @hello-pangea/dnd.

## Test Files Overview

### 1. drag-start.test.tsx (78 tests)

Tests drag initiation, data transfer, visual feedback, and accessibility announcements.

**Coverage Areas:**

- Drag Initiation (10 tests)
  - Mouse, touch, and keyboard drag starts
  - Left/right button handling
  - Disabled state handling

- Data Transfer Setup (10 tests)
  - Task ID and position data
  - Drag effect configuration
  - Special character handling

- Visual Feedback (10 tests)
  - Dragging class application
  - Opacity changes
  - Placeholder display
  - Animation transitions

- Accessibility Announcements (10 tests)
  - Screen reader support
  - aria-grabbed attributes
  - Keyboard instructions

- Edge Cases (10 tests)
  - Empty columns
  - Filtered views
  - Rapid operations

- Task Types (10 tests)
  - All status types
  - All priority levels
  - Tags and due dates

- Performance (5 tests)
  - Heavy boards
  - Memory leak prevention
  - Event throttling

- State Management (5 tests)
  - State tracking
  - State preservation

- Filters (5 tests)
  - Filter combinations

- Cancel Scenarios (3 tests)
  - Escape key
  - Mouse release
  - Premature end

### 2. drag-over.test.tsx (87 tests)

Tests drop zone highlighting, valid drop detection, scroll behavior, and drag-over state.

**Coverage Areas:**

- Drop Zone Highlighting (10 tests)
  - Column highlights
  - Visual indicators
  - Background changes

- Valid Drop Detection (10 tests)
  - All column types
  - Empty columns
  - Position detection

- Invalid Drop Prevention (10 tests)
  - Non-droppable areas
  - Disabled columns
  - Header/footer protection

- Scroll During Drag (10 tests)
  - Auto-scroll edges
  - Column scrolling
  - Speed adjustment

- Visual Feedback (10 tests)
  - Cursors
  - Placeholders
  - Animation

- Edge Cases (10 tests)
  - Empty columns
  - Rapid switching
  - Filter changes

- Performance (5 tests)
  - Efficient rendering
  - Event throttling

- Positions (7 tests)
  - First, middle, last positions

- Accessibility (5 tests)
  - Screen reader announcements
  - aria-dropeffect

- State Management (5 tests)
  - Drop target tracking

- Constraints (5 tests)
  - WIP limits
  - Permissions

### 3. drop.test.tsx (75 tests)

Tests successful drops, status updates, reordering, and drop cancellation.

**Coverage Areas:**

- Successful Drop Handling (10 tests)
  - Valid drops
  - Handler calls
  - Style cleanup

- Status Updates (10 tests)
  - All status transitions
  - Timestamp updates
  - completedAt handling

- Column Reordering (10 tests)
  - Same column moves
  - Cross-column moves
  - Task shifting

- Position Management (10 tests)
  - Beginning/middle/end
  - Adjacent moves
  - Index calculation

- Drop Cancellation (10 tests)
  - Outside zone drops
  - State rollback
  - Animation

- Filters (5 tests)
  - Active filter handling

- Edge Cases (10 tests)
  - Null destination
  - Rapid operations
  - Invalid IDs

- Performance (5 tests)
  - Efficient execution
  - Memory management

- Accessibility (5 tests)
  - Screen reader support
  - Focus management

### 4. multi-item.test.tsx (85 tests)

Tests multi-select drag, batch operations, selection state, and visual feedback.

**Coverage Areas:**

- Multi-Select Initiation (10 tests)
  - Ctrl/Cmd+Click
  - Shift+Click range
  - Select all

- Batch Move Operations (10 tests)
  - Moving selected tasks
  - Relative order
  - Status updates

- Selection State Management (10 tests)
  - State tracking
  - Clear selection
  - Persist on cancel

- Visual Feedback (10 tests)
  - Highlight selected
  - Count badge
  - Checkboxes

- Edge Cases (10 tests)
  - Empty columns
  - Rapid changes
  - Filter changes

- Performance (5 tests)
  - Large selections
  - Memory management

- Accessibility (5 tests)
  - Screen reader support
  - Keyboard shortcuts

- Batch Operations (10 tests)
  - Delete, priority, category
  - Tag addition
  - Due date updates

- UI Controls (10 tests)
  - Selection toolbar
  - Action menu

- Constraints (5 tests)
  - Mixed status prevention
  - WIP limits

### 5. dnd-edge-cases.test.js (70 tests) [E2E]

End-to-end tests for edge cases including same position drops, rapid operations, and error handling.

**Coverage Areas:**

- Same Position Drops (10 tests)
  - Exact same position
  - No API calls
  - Quick completion

- Same Column Different Position (10 tests)
  - Reordering
  - Status maintenance
  - Task shifting

- Rapid Operations (10 tests)
  - Quick succession
  - Operation queuing
  - State consistency

- During Loading (10 tests)
  - Disabled drag
  - Loading indicators
  - Queue operations

- After Error (10 tests)
  - API errors
  - Rollback
  - Retry logic

- Browser Compatibility (10 tests)
  - Safari, Firefox, Edge
  - Touch events
  - Screen sizes

- Memory & Performance (5 tests)
  - Memory leaks
  - Heavy boards
  - Cleanup

- Data Consistency (5 tests)
  - Concurrent modifications
  - Validation

## Total Test Coverage

- **Total Test Files**: 5
- **Total Tests**: 395
- **Target Coverage**: 95%+

## Test Categories Breakdown

| Category         | Tests |
| ---------------- | ----- |
| Drag Start       | 78    |
| Drag Over        | 87    |
| Drop             | 75    |
| Multi-Item       | 85    |
| Edge Cases (E2E) | 70    |

## Running the Tests

```bash
# Run all DND tests
npm test -- unit/frontend/dnd

# Run specific test file
npm test -- unit/frontend/dnd/drag-start.test.tsx

# Run with coverage
npm run test:coverage -- unit/frontend/dnd

# Run E2E edge cases
npm test -- e2e/scenarios/dnd-edge-cases.test.js

# Run in watch mode
npm run test:watch -- unit/frontend/dnd
```

## Test Structure

Each test follows the Arrange-Act-Assert pattern:

```typescript
it('should handle drag start on task card', () => {
  // Arrange: Set up test data and render component
  const mockBoard = boardFactory.typical();
  const { container } = renderWithProviders(
    <Board data={mockBoard} {...mockHandlers} filters={{}} />
  );

  // Act: Perform the action
  const taskCard = container.querySelector('[draggable="true"]');

  // Assert: Verify the outcome
  expect(taskCard).toBeDefined();
});
```

## Dependencies

- **vitest**: Test runner
- **@testing-library/react**: Component testing utilities
- **@hello-pangea/dnd**: Drag and drop library
- **jsdom**: Browser environment simulation

## Factories

Test data is generated using factories in `tests/helpers/factories.ts`:

- `taskFactory`: Create task objects with various properties
- `boardFactory`: Create board states (empty, typical, heavy)
- `columnFactory`: Create column structures

## Test Utilities

Custom utilities in `tests/helpers/test-utils.tsx`:

- `renderWithProviders`: Wraps components with DragDropContext
- `clickElement`: Simulates click events
- `mockFetchResponse`: Mocks API responses
- `mockFetchError`: Mocks API errors

## Coverage Goals

- Lines: 95%
- Branches: 90%
- Functions: 95%
- Statements: 95%

## Key Testing Patterns

1. **Test Behavior, Not Implementation**: Focus on what users see and do
2. **Arrange-Act-Assert**: Clear test structure
3. **Deterministic Tests**: No flakiness or randomness
4. **Fast Feedback**: Parallel execution where possible
5. **Comprehensive Edge Cases**: Cover all scenarios

## Accessibility Testing

All drag-and-drop operations include accessibility tests:

- Screen reader announcements
- Keyboard navigation
- ARIA attributes
- Focus management

## Performance Testing

Performance benchmarks included:

- Heavy board handling (1000+ tasks)
- Memory leak prevention
- Event throttling
- Efficient re-renders

## Future Enhancements

- [ ] Add visual regression tests
- [ ] Add integration tests with real API
- [ ] Add touch device specific tests
- [ ] Add animation timing tests
- [ ] Add undo/redo functionality tests
