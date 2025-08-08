# QVF Platform E2E Testing Suite

This comprehensive end-to-end testing suite provides complete test coverage for the QVF Platform using Playwright. The test suite includes authentication flows, dashboard navigation, QVF scoring workflows, work item management, stakeholder comparison, visual regression testing, performance monitoring, mobile responsive testing, and API integration testing.

## 📋 Table of Contents

- [Test Suite Overview](#test-suite-overview)
- [Quick Start](#quick-start)
- [Test Categories](#test-categories)
- [Running Tests](#running-tests)
- [CI/CD Integration](#cicd-integration)
- [Test Configuration](#test-configuration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🧪 Test Suite Overview

### Coverage Areas
- **Authentication & Authorization**: Login/logout for all 4 user roles
- **Dashboard Navigation**: Role-based access control and navigation
- **QVF Scoring Workflow**: Complete QVF calculation and scoring process  
- **Work Item Management**: CRUD operations for work items
- **Stakeholder Comparison**: Multi-stakeholder QVF comparison interface
- **Visual Regression**: Screenshot-based visual consistency testing
- **Performance Testing**: Page load times and API response monitoring
- **Mobile Responsive**: Cross-device and viewport testing
- **API Integration**: Frontend-backend integration validation

### Browser Support
- ✅ Chromium/Chrome
- ✅ Firefox
- ✅ WebKit/Safari
- ✅ Mobile Chrome
- ✅ Mobile Safari
- ✅ Tablet viewports

### User Roles Tested
- **Executive**: Strategic dashboard access, portfolio view
- **Product Owner**: Backlog management, QVF scoring, comparison
- **Scrum Master**: Sprint management, team metrics
- **Developer**: Work item access, task updates

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- pnpm 8+
- Docker (optional, for containerized testing)

### Installation
```bash
# Clone and navigate to project
cd qvf-platform

# Install dependencies
pnpm install
pip install -r apps/api/requirements.txt

# Install Playwright browsers
pnpm exec playwright install --with-deps
```

### Run Smoke Tests
```bash
# Quick smoke test (5-10 minutes)
./scripts/run-tests.sh smoke chromium

# Or using pnpm script
pnpm test:e2e:smoke
```

### Run Full Test Suite
```bash
# All tests across all browsers (30-45 minutes)
./scripts/run-tests.sh all

# Specific test suite
./scripts/run-tests.sh auth chromium
./scripts/run-tests.sh dashboard firefox
```

## 📊 Test Categories

### 1. Authentication Tests (`tests/auth/`)
- **authentication.spec.ts**: Complete auth flow testing
- ✅ Login validation for all roles
- ✅ Invalid credential handling
- ✅ Session persistence
- ✅ Token expiration handling
- ✅ Concurrent session management

```bash
# Run authentication tests
./scripts/run-tests.sh auth
```

### 2. Dashboard Navigation Tests (`tests/dashboard/`)
- **navigation.spec.ts**: Role-based dashboard access
- ✅ Executive dashboard features
- ✅ Product Owner dashboard functionality
- ✅ Scrum Master dashboard access
- ✅ Developer work item interface
- ✅ Role-based access control
- ✅ Navigation accessibility

```bash
# Run dashboard tests
./scripts/run-tests.sh dashboard
```

### 3. QVF Scoring Tests (`tests/qvf/`)
- **scoring-workflow.spec.ts**: Complete QVF workflow
- ✅ QVF calculation interface access
- ✅ Work item input and validation
- ✅ Scoring algorithm execution
- ✅ Results display and visualization
- ✅ Bulk operations support
- ✅ Export functionality
- ✅ Error handling

```bash
# Run QVF scoring tests
./scripts/run-tests.sh qvf
```

### 4. Work Items CRUD Tests (`tests/work-items/`)
- **crud-operations.spec.ts**: Complete work item management
- ✅ Create new work items
- ✅ Read/display work items list
- ✅ Update existing work items
- ✅ Delete work items with confirmation
- ✅ Bulk operations
- ✅ Form validation
- ✅ Search and filtering

```bash
# Run work items tests
./scripts/run-tests.sh work-items
```

### 5. Stakeholder Comparison Tests (`tests/comparison/`)
- **stakeholder-comparison.spec.ts**: Multi-stakeholder QVF comparison
- ✅ Comparison interface access
- ✅ Stakeholder input selection
- ✅ Pairwise comparison matrix
- ✅ Progress tracking
- ✅ Consistency indicators
- ✅ Role-based perspectives
- ✅ Results export
- ✅ Real-time collaboration

```bash
# Run comparison tests
./scripts/run-tests.sh comparison
```

### 6. Visual Regression Tests (`tests/visual/`)
- **visual-regression.spec.ts**: Screenshot-based visual testing
- ✅ Page layout consistency
- ✅ Component visual baseline
- ✅ Cross-viewport compatibility
- ✅ Theme and styling verification
- ✅ Error state visuals
- ✅ Data visualization consistency
- ✅ Accessibility visual standards

```bash
# Run visual regression tests
./scripts/run-tests.sh visual
```

### 7. Performance Tests (`tests/performance/`)
- **performance.spec.ts**: Performance and load monitoring
- ✅ Page load time budgets
- ✅ API response time monitoring
- ✅ Resource loading efficiency
- ✅ Memory usage tracking
- ✅ Network condition handling
- ✅ User interaction responsiveness
- ✅ Concurrent user simulation

```bash
# Run performance tests
./scripts/run-tests.sh performance
```

### 8. Mobile Responsive Tests (`tests/mobile/`)
- **responsive.spec.ts**: Cross-device compatibility
- ✅ Mobile device login flows
- ✅ Touch-friendly interface validation
- ✅ Viewport adaptation
- ✅ Orientation change handling
- ✅ Mobile-specific features
- ✅ Performance on mobile networks
- ✅ Accessibility on mobile

```bash
# Run mobile tests
./scripts/run-tests.sh mobile
```

### 9. API Integration Tests (`tests/api/`)
- **integration.spec.ts**: Frontend-backend integration
- ✅ Authentication API validation
- ✅ Work Items API CRUD operations
- ✅ QVF Scoring API integration
- ✅ Role-based access control
- ✅ Error handling and validation
- ✅ Data persistence verification
- ✅ Response format consistency

```bash
# Run API integration tests
./scripts/run-tests.sh api
```

## 🏃‍♂️ Running Tests

### Local Development
```bash
# Interactive test runner with UI
pnpm exec playwright test --ui

# Run specific test file
pnpm exec playwright test tests/auth/authentication.spec.ts

# Debug mode with browser visible
./scripts/run-tests.sh auth chromium false true

# Run tests in headed mode
pnpm exec playwright test --headed
```

### Test Scripts Available
```bash
# Main test runner script
./scripts/run-tests.sh [suite] [browser] [headless] [debug]

# Docker-based testing
./scripts/test-docker.sh [suite] [browser]

# Package.json scripts
pnpm test:e2e              # Full test suite
pnpm test:e2e:smoke        # Smoke tests only
pnpm test:e2e:headed       # Tests with browser visible
pnpm test:e2e:debug        # Debug mode
```

### Test Suite Options
- **all**: Complete test suite (default)
- **smoke**: Quick validation tests (auth + dashboard)
- **auth**: Authentication and authorization tests
- **dashboard**: Dashboard navigation and role-based access
- **qvf**: QVF scoring workflow tests
- **work-items**: Work item management CRUD tests
- **comparison**: Stakeholder comparison interface tests
- **visual**: Visual regression and screenshot tests
- **performance**: Performance and load tests
- **mobile**: Mobile responsive and device tests
- **api**: API integration tests

### Browser Options
- **chromium**: Google Chrome/Chromium (default)
- **firefox**: Mozilla Firefox
- **webkit**: Safari/WebKit
- **all**: Run tests across all browsers

## 🔄 CI/CD Integration

### GitHub Actions Workflow
The project includes a comprehensive GitHub Actions workflow (`.github/workflows/e2e-tests.yml`) that:
- ✅ Runs on push to main/develop branches
- ✅ Runs on pull requests
- ✅ Supports manual workflow dispatch with test suite selection
- ✅ Runs daily scheduled tests
- ✅ Matrix testing across browsers
- ✅ Artifact collection and reporting
- ✅ Mobile-specific test jobs

### Workflow Triggers
```yaml
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  workflow_dispatch:     # Manual trigger with options
```

### Manual Workflow Dispatch
1. Go to GitHub Actions tab
2. Select "QVF Platform E2E Tests" workflow
3. Click "Run workflow"
4. Choose test suite (all, smoke, auth, dashboard, etc.)
5. Monitor execution and download artifacts

## ⚙️ Test Configuration

### Playwright Configuration (`playwright.config.ts`)
```typescript
// Key configuration highlights
export default defineConfig({
  testDir: './tests',
  timeout: 60000,              // 60 seconds per test
  expect: { timeout: 15000 },  // 15 seconds for assertions
  retries: process.env.CI ? 2 : 1,
  workers: process.env.CI ? 2 : 4,
  
  // Multiple reporters for comprehensive reporting
  reporter: [
    ['html', { outputFolder: 'test-results/html-report' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/results.xml' }]
  ],
  
  // Projects for different browsers and test types
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    { name: 'chromium', use: devices['Desktop Chrome'] },
    { name: 'firefox', use: devices['Desktop Firefox'] },
    { name: 'webkit', use: devices['Desktop Safari'] },
    { name: 'mobile-chrome', use: devices['Pixel 5'] },
    { name: 'api', testMatch: '**/api/*.spec.ts' }
  ]
})
```

### Environment Variables
```bash
# Service URLs
BASE_URL=http://localhost:3006          # Frontend URL
API_BASE_URL=http://localhost:8000      # Backend API URL

# Test Configuration  
NODE_ENV=test                           # Environment
CI=true                                 # CI mode flag
PLAYWRIGHT_HTML_REPORT=test-results/html-report

# Authentication (for API tests)
JWT_SECRET_KEY=test-secret-key-for-e2e-tests
```

### Test Users
The test suite uses predefined test users with specific roles:
```typescript
// Available in tests/fixtures/test-users.ts
TestUsers = {
  executive: { username: 'executive', password: 'executive123' },
  productOwner: { username: 'product_owner', password: 'po123' },
  scrumMaster: { username: 'scrum_master', password: 'sm123' },
  developer: { username: 'developer', password: 'dev123' }
}
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Tests Failing Due to Services Not Ready
```bash
# Increase timeout in scripts/run-tests.sh
wait_for_service "http://localhost:8000/health" 60 "API server"
wait_for_service "http://localhost:3006" 120 "Web server"

# Check service logs
tail -f apps/api/api.log
tail -f apps/web/web.log
```

#### 2. Browser Installation Issues
```bash
# Reinstall browsers
pnpm exec playwright install --with-deps chromium firefox webkit

# For specific browser
pnpm exec playwright install chromium
```

#### 3. Port Conflicts
```bash
# Kill processes on required ports
lsof -ti:8000 | xargs kill -9
lsof -ti:3006 | xargs kill -9

# Or use different ports
export BASE_URL=http://localhost:3007
export API_BASE_URL=http://localhost:8001
```

#### 4. Database Issues
```bash
# Reset test database
rm apps/api/test.db
./scripts/run-tests.sh smoke  # Will recreate database
```

#### 5. Visual Regression Failures
```bash
# Update visual baselines (be careful!)
pnpm exec playwright test --update-snapshots tests/visual/

# Run visual tests in headed mode to inspect
pnpm exec playwright test tests/visual/ --headed
```

#### 6. Performance Test Failures
```bash
# Run performance tests in isolation
./scripts/run-tests.sh performance chromium

# Check system resources during tests
htop  # or equivalent system monitor
```

### Debug Mode
```bash
# Run tests in debug mode with browser visible
./scripts/run-tests.sh auth chromium false true

# Playwright debug mode
pnpm exec playwright test --debug tests/auth/authentication.spec.ts

# Trace viewer for failed tests
pnpm exec playwright show-trace test-results/traces/trace.zip
```

### Test Reports and Artifacts

#### HTML Report
```bash
# Open interactive HTML report
open test-results/html-report/index.html
# or
pnpm exec playwright show-report
```

#### Screenshots and Videos
- Screenshots: `test-results/screenshots/`
- Videos: `test-results/videos/` (only for failed tests)
- Traces: `test-results/traces/` (for debugging)

#### JSON Results
```bash
# Programmatic access to test results
cat test-results/results.json | jq '.stats'
```

## 🤝 Contributing

### Adding New Tests
1. Choose appropriate test category directory
2. Follow existing naming conventions (`*.spec.ts`)
3. Use shared fixtures from `tests/fixtures/`
4. Include proper test descriptions and assertions
5. Add screenshot captures for visual verification
6. Update this README if adding new test categories

### Test Writing Guidelines
```typescript
// Use descriptive test names
test('should allow product owner to create work item with QVF scoring', async ({ page }) => {
  // Use shared fixtures
  await login(page, TestUsers.productOwner);
  
  // Take screenshots for documentation
  await takeScreenshot(page, 'work-item-creation-form');
  
  // Use robust selectors
  await page.click('[data-testid="create-work-item"]');
  
  // Clear assertions
  await expect(page.locator('.success-message')).toContainText('Work item created');
});
```

### Running Tests Before Commit
```bash
# Run smoke tests before committing
./scripts/run-tests.sh smoke

# Run affected test suites
./scripts/run-tests.sh auth
./scripts/run-tests.sh dashboard
```

## 📚 Additional Resources

### Playwright Documentation
- [Playwright Official Docs](https://playwright.dev/)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [Debugging Guide](https://playwright.dev/docs/debug)

### QVF Platform Specific
- [API Documentation](./BACKEND_IMPLEMENTATION_COMPLETE.md)
- [Frontend Architecture](./FRONTEND_IMPLEMENTATION_COMPLETE.md)
- [Deployment Guide](./DEPLOYMENT_GUIDE.md)

---

## 📞 Support

For questions or issues with the E2E testing suite:
1. Check the troubleshooting section above
2. Review test logs in `test-results/`
3. Check GitHub Actions workflow runs
4. Review individual test files for specific functionality

**Happy Testing! 🧪✨**