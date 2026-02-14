# Quick Start Guide - Test Suite

Get started with the Kanban Mission Control test suite in 5 minutes.

---

## Installation (2 minutes)

```bash
# Navigate to tests directory
cd /Users/arvindsarin/Cursor/Claude-2026/openclaw/tools/kanban/tests

# Install dependencies
npm install

# Verify installation
npm test -- --version
```

---

## Run Your First Tests (1 minute)

```bash
# Run sample tests
npm test

# Run with verbose output
npm run test:unit -- --reporter=verbose

# Run specific test file
npm test -- unit/server/routes/tasks-get.test.js
```

---

## View Coverage (1 minute)

```bash
# Generate coverage report
npm run test:coverage

# Open coverage report in browser
open coverage/index.html
```

---

## Watch Mode (Development)

```bash
# Start watch mode
npm run test:watch

# Tests will re-run on file changes
# Press 'a' to run all tests
# Press 'p' to filter by filename
# Press 'q' to quit
```

---

## Next Steps

1. **Read the docs:**
   - [TEST-PLAN.md](./TEST-PLAN.md) - Overall strategy
   - [TEST-COUNT-BREAKDOWN.md](./TEST-COUNT-BREAKDOWN.md) - Test inventory
   - [IMPLEMENTATION-GUIDE.md](./IMPLEMENTATION-GUIDE.md) - How to implement

2. **Explore sample tests:**
   - `unit/server/routes/tasks-get.test.js` - Backend API tests
   - `unit/frontend/components/TaskCard.test.tsx` - Component tests
   - `unit/frontend/hooks/useKanban.test.ts` - Hook tests
   - `integration/api/task-crud-flow.test.js` - Integration tests

3. **Start implementing:**
   - Follow the IMPLEMENTATION-GUIDE.md phase by phase
   - Use factories from `helpers/factories.ts`
   - Check TEST-COUNT-BREAKDOWN.md for progress tracking

---

## Common Commands

```bash
# Run all tests
npm test

# Run unit tests only
npm run test:unit

# Run integration tests only
npm run test:integration

# Run E2E tests only
npm run test:e2e

# Run sanity suite (fast)
npm run test:sanity

# Run with UI
npm run test:ui

# Debug tests
npm run test:debug

# Check coverage thresholds
npm run coverage:check
```

---

## Directory Structure

```
tests/
├── unit/               Unit tests (7,000)
├── integration/        Integration tests (2,000)
├── e2e/               E2E tests (1,000)
├── fixtures/          Test data
├── mocks/            Mocked dependencies
├── helpers/          Test utilities
├── config/           Vitest configurations
├── TEST-PLAN.md       📖 Main documentation
├── IMPLEMENTATION-GUIDE.md 📖 Implementation steps
├── ARCHITECTURE.md    📖 Visual architecture
└── README.md          📖 Detailed README
```

---

## Tips

💡 **Use factories** instead of creating test data manually
💡 **Run sanity tests** before committing
💡 **Check coverage** to find untested code
💡 **Use watch mode** during development
💡 **Read sample tests** to understand patterns

---

## Help & Support

- Read the full [README.md](./README.md)
- Check [ARCHITECTURE.md](./ARCHITECTURE.md) for visual guides
- Review sample tests for patterns
- See [IMPLEMENTATION-GUIDE.md](./IMPLEMENTATION-GUIDE.md) for detailed steps

---

**Ready to start?** Pick a test category from [TEST-COUNT-BREAKDOWN.md](./TEST-COUNT-BREAKDOWN.md) and begin implementing!
