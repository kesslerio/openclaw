# Kanban Mission Control Test Suite

Enterprise-grade comprehensive test suite with 10,000+ tests targeting 95%+ code coverage.

## Quick Start

```bash
# Install dependencies
npm install

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch

# Run only unit tests
npm run test:unit

# Run only integration tests
npm run test:integration

# Run only E2E tests
npm run test:e2e

# Run sanity suite (fast, critical tests only)
npm run test:sanity
```

## Test Structure

```
tests/
├── unit/               Unit tests (70% - 7,000 tests)
│   ├── server/         Backend unit tests
│   └── frontend/       Frontend unit tests
├── integration/        Integration tests (20% - 2,000 tests)
│   ├── api/           API integration tests
│   └── data/          Data layer tests
├── e2e/               E2E tests (10% - 1,000 tests)
│   ├── flows/         User flow tests
│   └── scenarios/     Complex scenario tests
├── fixtures/          Test data
├── mocks/            Mocked dependencies
├── helpers/          Test utilities
└── config/           Test configurations
```

## Documentation

- **[TEST-PLAN.md](./TEST-PLAN.md)** - Comprehensive test strategy and architecture
- **[TEST-COUNT-BREAKDOWN.md](./TEST-COUNT-BREAKDOWN.md)** - Detailed breakdown of all 10,000+ tests

## Test Categories

### Unit Tests (7,000 tests)

**Backend (2,500 tests)**

- API route handlers
- Business logic services
- Middleware and utilities

**Frontend (4,500 tests)**

- React components
- Custom hooks
- Frontend utilities

### Integration Tests (2,000 tests)

- API integration flows
- Data persistence layer
- Gateway integration
- Concurrent operations

### E2E Tests (1,000 tests)

- User workflow tests
- Multi-user scenarios
- Performance tests
- Edge case scenarios

## Coverage Targets

| Category | Lines | Branches | Functions | Statements |
| -------- | ----- | -------- | --------- | ---------- |
| Overall  | 95%+  | 90%+     | 95%+      | 95%+       |

## Test Execution

### Daily Development

```bash
# Run sanity suite before commit (< 5 min)
npm run test:sanity

# Run unit tests during development
npm run test:unit:watch
```

### Pull Requests

```bash
# Run unit + integration tests
npm run test:unit
npm run test:integration
```

### CI/CD Pipeline

```bash
# Full suite with coverage
npm run test:ci
npm run coverage:check
```

## Writing Tests

### Test Naming Convention

```javascript
describe("ComponentName / FunctionName", () => {
  describe("Feature / Scenario", () => {
    it("should do something specific", () => {
      // Test implementation
    });
  });
});
```

### Using Factories

```javascript
import { taskFactory, boardFactory } from "./helpers/factories";

// Create a task with defaults
const task = taskFactory.build();

// Create a task with overrides
const urgentTask = taskFactory.build({ priority: "high" });

// Create multiple tasks
const tasks = taskFactory.buildMany(10);

// Use convenience methods
const overdueTask = taskFactory.overdue();
const completedTask = taskFactory.completed();
```

### Using Test Utils

```javascript
import { renderWithProviders, waitFor } from "./helpers/test-utils";

it("should render component", async () => {
  const { getByText } = renderWithProviders(<MyComponent />);
  await waitFor(() => {
    expect(getByText("Expected Text")).toBeDefined();
  });
});
```

## Test Configuration

### Unit Tests

- Environment: jsdom
- Timeout: 5 seconds
- Concurrency: 32
- Mocks: All external dependencies

### Integration Tests

- Environment: node + jsdom
- Timeout: 30 seconds
- Concurrency: 8
- Real dependencies: Gateway on port 18789

### E2E Tests

- Environment: Playwright
- Timeout: 60 seconds
- Concurrency: 4
- Real browser interactions

## CI/CD Integration

### GitHub Actions

The test suite integrates with GitHub Actions:

1. **Sanity** (5 min) - Critical tests on every commit
2. **Unit** (15 min) - All unit tests on PR
3. **Integration** (20 min) - Integration tests on PR
4. **E2E** (30 min) - Full E2E suite on main branch
5. **Coverage** - Upload to Codecov

### Pre-commit Hooks

```bash
# Install pre-commit hooks
npm run prepare

# Hooks will run:
# - Sanity test suite
# - Linting
# - Type checking
```

## Troubleshooting

### Tests Timing Out

```bash
# Increase timeout for specific test
it('slow test', async () => {
  // test code
}, 30000); // 30 second timeout
```

### Flaky Tests

```bash
# Run test multiple times to identify flakiness
npm test -- --run --repeat=10 path/to/test.test.ts
```

### Debug Mode

```bash
# Run tests with debugger
npm run test:debug

# In Chrome, navigate to: chrome://inspect
```

### Coverage Issues

```bash
# Generate detailed coverage report
npm run coverage:report

# Check specific file coverage
npm test -- --coverage --coverageReporter=text path/to/file.test.ts
```

## Performance

### Test Execution Times

| Suite          | Tests      | Time         |
| -------------- | ---------- | ------------ |
| Sanity         | 300        | < 5 min      |
| Unit           | 7,000      | < 15 min     |
| Integration    | 2,000      | < 20 min     |
| E2E            | 1,000      | < 30 min     |
| **Full Suite** | **10,000** | **< 60 min** |

### Optimization Tips

1. **Run tests in parallel**: Vitest runs tests concurrently by default
2. **Use test.concurrent**: For independent tests
3. **Mock expensive operations**: File I/O, network calls
4. **Use test fixtures**: Pre-generated test data
5. **Skip E2E in development**: Run only on CI

## Best Practices

### DO

- ✅ Test behavior, not implementation
- ✅ Use descriptive test names
- ✅ Keep tests isolated and independent
- ✅ Use factories for test data
- ✅ Mock external dependencies in unit tests
- ✅ Test edge cases and error paths
- ✅ Maintain high coverage

### DON'T

- ❌ Test internal implementation details
- ❌ Share state between tests
- ❌ Write flaky tests
- ❌ Skip error case testing
- ❌ Write tests without assertions
- ❌ Ignore test failures

## Contributing

When adding new functionality:

1. Write tests first (TDD)
2. Ensure all tests pass
3. Maintain coverage above 95%
4. Update TEST-COUNT-BREAKDOWN.md
5. Run full suite before PR

## Resources

- [Vitest Documentation](https://vitest.dev/)
- [Testing Library](https://testing-library.com/)
- [Playwright Documentation](https://playwright.dev/)
- [Test Patterns](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)

---

**Status:** Test suite design complete, implementation in progress
**Target:** 10,000+ tests with 95%+ coverage
**Current:** TBD tests (TBD% coverage)
