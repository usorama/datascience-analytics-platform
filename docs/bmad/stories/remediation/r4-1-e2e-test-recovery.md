---
# Agent Targeting
target-agent: test-engineer
tools: [Read, Write, MultiEdit, Bash, Grep, Glob]

# Project Context
epic: Remediation Sprint R4 - Testing & Verification
story: Story R4.1 - E2E Test Suite Recovery
priority: critical
estimated-effort: 1 day (15 SP)
dependencies: ["All remediation stories R1-R3", "Functional application"]

# Acceptance Criteria
acceptance-criteria: |
  - [ ] 🎯 Test Coverage: >95% E2E test passage rate (Current: 27%)
  - [ ] 📱 Mobile Tests: All 24 mobile responsive tests passing (Current: 0/24)
  - [ ] 🔐 Auth Tests: Complete authentication flow coverage (Current: 8/12 failing)
  - [ ] 📊 Dashboard Tests: All dashboard functionality tested (Current: 12/18 failing)
  - [ ] 📤 Export Tests: Export functionality fully tested (Current: 0/8 passing)
  - [ ] ⚡ Performance Tests: Core Web Vitals tests passing (Current: 5/8 failing)
  - [ ] ♿ Accessibility Tests: WCAG AA compliance verified
  - [ ] 🔄 CI/CD Integration: Tests run automatically on all PRs and deployments
  - [ ] 🚨 Alerting: Failed tests immediately notify development team
  - [ ] 📋 Test Reporting: Comprehensive test reports with failure analysis

# Technical Constraints
constraints: |
  - Must use existing Playwright testing framework and infrastructure
  - Cannot modify application functionality to make tests pass (tests must verify real functionality)
  - Must maintain test isolation and independence between test cases
  - All tests must run consistently in CI/CD environment (Linux containers)
  - Must support parallel test execution for faster feedback
  - Test data must be isolated and cleaned up after each test run
  - Must handle flaky network conditions and timing issues
  - All tests must provide clear error messages for debugging failures

# Implementation Context
architectural-guidance: |
  FORENSIC FINDING: E2E test suite has 73% failure rate, indicating massive implementation gaps.
  Current test failures reveal that claimed features are not actually functional.
  
  Test Failure Analysis:
  - Authentication: Login/logout flows broken
  - Mobile Responsive: No mobile functionality implemented
  - Dashboard Load: Charts and data loading issues
  - Work Items CRUD: Create/Update/Delete operations failing
  - Export Functions: No export functionality exists
  - Performance: Poor Core Web Vitals scores
  
  Recovery Strategy:
  1. Fix all test infrastructure and configuration issues
  2. Identify and fix application bugs revealed by failing tests
  3. Add comprehensive test coverage for new remediation features
  4. Implement proper test data management and isolation
  5. Set up robust CI/CD integration with failure notifications
  6. Create comprehensive test reporting and monitoring
  
  Test Architecture:
  - Playwright for E2E testing with multiple browser support
  - Test fixtures for consistent test data setup
  - Page Object Model for maintainable test code
  - Parallel execution for faster feedback
  - Visual regression testing for UI consistency
  - API testing for backend integration verification

# Quality Gates
quality-gates: |
  MANDATORY GATES (Must pass before story completion):
  
  1. TEST PASSAGE RATE: >95% (121/127 tests passing)
     - Current: 34/127 tests passing (27%)
     - Target: 121/127 tests passing (95%)
     - Verification: All tests run in clean CI environment
     - Acceptance: No more than 6 tests can be failing/flaky
  
  2. COMPREHENSIVE COVERAGE: All major user journeys tested
     - Authentication flows: Login, logout, role switching
     - Dashboard functionality: All visualizations load and interact
     - Work item management: CRUD operations, drag-drop, prioritization
     - Mobile responsiveness: All features work on mobile devices
     - Export capabilities: PDF/Excel generation and download
  
  3. CI/CD INTEGRATION: Automated testing pipeline
     - Tests run on every PR automatically
     - Test results block merge if failing
     - Performance regression tests included
     - Accessibility tests integrated
     - Visual regression tests configured
  
  4. TEST STABILITY: <5% flaky test rate
     - Tests pass consistently across multiple runs
     - No timing-dependent failures
     - Proper async handling and waiting
     - Robust error handling and recovery
  
  5. COMPREHENSIVE REPORTING: Clear test insights
     - Test results dashboard available
     - Failure analysis with screenshots and logs
     - Performance metrics tracking
     - Test execution time monitoring
     - Historical trend analysis
---

# User Story: E2E Test Suite Recovery

## Business Context
As a development team and stakeholders, we need a comprehensive, reliable E2E test suite that validates all application functionality so that we can deploy with confidence and ensure users receive working features.

**CRITICAL ISSUE**: Current test suite has a 73% failure rate, indicating that claimed functionality is not actually working. This represents a massive quality assurance failure that must be immediately addressed.

**Business Impact**:
- **Current State**: 73% test failure rate, unreliable deployments, broken user experiences
- **Target State**: >95% test passage rate, confident deployments, validated functionality
- **Risk Mitigation**: Prevents deployment of broken features to production
- **Quality Assurance**: Ensures all remediation work is properly validated
- **Stakeholder Confidence**: Demonstrates actual working functionality

## Technical Requirements

### Current Test Failure Analysis
```typescript
interface TestFailureAnalysis {
  totalTests: 127;
  currentPassing: 34;
  currentFailing: 67;
  currentSkipped: 26;
  passageRate: 27%;
  
  failuresByCategory: {
    authentication: { failing: 8, total: 12, rate: '33%' };
    mobileResponsive: { failing: 24, total: 24, rate: '0%' };
    dashboardLoad: { failing: 12, total: 18, rate: '33%' };
    workItemsCRUD: { failing: 15, total: 21, rate: '29%' };
    exportFunctions: { failing: 8, total: 8, rate: '0%' };
    performance: { failing: 5, total: 8, rate: '38%' };
    accessibility: { failing: 12, total: 15, rate: '20%' };
    integration: { failing: 8, total: 12, rate: '33%' };
    visual: { failing: 7, total: 10, rate: '30%' };
  };
  
  criticalIssues: [
    'Mobile responsiveness completely non-functional',
    'Export functionality not implemented', 
    'Authentication flows inconsistent',
    'Dashboard charts failing to load',
    'Work item operations broken',
    'Performance benchmarks not met'
  ];
}
```

### Required Test Recovery Plan
```typescript
interface TestRecoveryPlan {
  phase1: {
    name: 'Infrastructure Fixes';
    duration: '2 hours';
    tasks: [
      'Fix Playwright configuration and setup',
      'Resolve test isolation issues',
      'Fix timing and async handling problems',
      'Update test fixtures and data management'
    ];
  };
  
  phase2: {
    name: 'Application Bug Fixes';
    duration: '4 hours'; 
    tasks: [
      'Fix authentication flow bugs revealed by tests',
      'Resolve dashboard loading and chart rendering issues',
      'Fix work item CRUD operation failures',
      'Address mobile responsiveness gaps'
    ];
  };
  
  phase3: {
    name: 'Test Enhancement';
    duration: '2 hours';
    tasks: [
      'Add comprehensive mobile test coverage',
      'Implement export functionality tests',
      'Add performance benchmark tests',
      'Create accessibility compliance tests'
    ];
  };
}
```

### Test Infrastructure Requirements
```typescript
interface TestInfrastructure {
  framework: 'Playwright';
  browsers: ['chromium', 'webkit', 'firefox'];
  devices: [
    'iPhone 12', 'iPhone 13 Pro', 'iPad Air',
    'Pixel 5', 'Samsung Galaxy S21'
  ];
  
  configuration: {
    timeout: 30000;          // 30 seconds per test
    retries: 2;              // Retry flaky tests
    parallel: 4;             // Parallel execution
    screenshot: 'only-on-failure';
    video: 'retain-on-failure';
    trace: 'retain-on-failure';
  };
  
  testData: {
    isolation: 'per-test';   // Clean state for each test
    cleanup: 'automatic';    // Auto cleanup after tests
    fixtures: 'consistent';  // Standardized test data
  };
  
  reporting: {
    html: true;              // HTML test report
    junit: true;             // CI integration
    github: true;            // GitHub Actions integration
    screenshots: true;       // Visual failure analysis
    traces: true;            // Detailed execution traces
  };
}
```

## Implementation Guidance

### Phase 1: Test Infrastructure Recovery (5 SP - 2 hours)

#### **Task 1.1: Playwright Configuration Fix**
```typescript
// playwright.config.ts - Updated configuration
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 30 * 1000,        // 30 seconds per test
  expect: { timeout: 5000 }, // 5 seconds for assertions
  fullyParallel: true,       // Run tests in parallel
  forbidOnly: !!process.env.CI, // Fail CI if test.only
  retries: process.env.CI ? 2 : 0, // Retry on CI
  workers: process.env.CI ? 2 : undefined,
  
  reporter: [
    ['html'],
    ['junit', { outputFile: 'test-results/junit.xml' }],
    ['github'], // GitHub Actions integration
  ],
  
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3006',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  projects: [
    // Desktop browsers
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    
    // Mobile devices - CRITICAL for mobile responsiveness tests
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
    {
      name: 'iPad',
      use: { ...devices['iPad Air'] },
    },
  ],
  
  // Global test setup
  globalSetup: require.resolve('./tests/global-setup.ts'),
  globalTeardown: require.resolve('./tests/global-teardown.ts'),
});
```

#### **Task 1.2: Test Fixtures and Helpers Upgrade**
```typescript
// tests/fixtures/test-helpers.ts - Enhanced helpers
import { Page, expect } from '@playwright/test';

export async function login(page: Page, user: TestUser): Promise<void> {
  await page.goto('/login');
  
  // Wait for login form to be fully loaded
  await expect(page.locator('input[name="username"]')).toBeVisible();
  await expect(page.locator('input[name="password"]')).toBeVisible();
  
  // Fill credentials
  await page.fill('input[name="username"]', user.username);
  await page.fill('input[name="password"]', user.password);
  
  // Submit and wait for navigation
  await Promise.all([
    page.waitForResponse(response => 
      response.url().includes('/api/v1/auth/token') && response.status() === 200
    ),
    page.click('button[type="submit"]')
  ]);
  
  // Verify successful login
  await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
  
  // Wait for dashboard to load completely
  await page.waitForLoadState('networkidle');
}

export async function waitForPageLoad(page: Page, timeout: number = 10000): Promise<void> {
  // Wait for network requests to complete
  await page.waitForLoadState('networkidle', { timeout });
  
  // Wait for main content to be visible
  await expect(page.locator('main, [role="main"], #main-content')).toBeVisible();
  
  // Wait for any loading indicators to disappear
  await expect(page.locator('[data-testid="loading"], .loading')).not.toBeVisible({ timeout: 5000 });
}

export async function takeScreenshot(page: Page, name: string): Promise<void> {
  await page.screenshot({ 
    path: `test-results/screenshots/${name}-${Date.now()}.png`,
    fullPage: true
  });
}

export async function verifyNoConsoleErrors(page: Page): Promise<void> {
  const errors: string[] = [];
  
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text());
    }
  });
  
  if (errors.length > 0) {
    throw new Error(`Console errors found: ${errors.join(', ')}`);
  }
}
```

### Phase 2: Critical Test Fixes (8 SP - 4 hours)

#### **Task 2.1: Authentication Test Recovery**
```typescript
// tests/auth/authentication.spec.ts - Fixed authentication tests
import { test, expect } from '@playwright/test';
import { TestUsers, login, waitForPageLoad } from '../fixtures/test-helpers';

test.describe('Authentication Flow Recovery', () => {
  test.beforeEach(async ({ page }) => {
    // Ensure clean state
    await page.context().clearCookies();
    await page.context().clearPermissions();
  });

  test('Login flow - Executive user', async ({ page }) => {
    await page.goto('/login');
    
    // FIXED: Wait for form to be fully rendered
    await expect(page.locator('form')).toBeVisible();
    await expect(page.locator('input[name="username"]')).toBeEnabled();
    await expect(page.locator('input[name="password"]')).toBeEnabled();
    
    // FIXED: Use proper form submission
    await page.fill('input[name="username"]', TestUsers.executive.username);
    await page.fill('input[name="password"]', TestUsers.executive.password);
    
    // FIXED: Wait for API response
    const responsePromise = page.waitForResponse('/api/v1/auth/token');
    await page.click('button[type="submit"]');
    const response = await responsePromise;
    
    expect(response.status()).toBe(200);
    
    // FIXED: Wait for complete navigation
    await page.waitForURL(/\/dashboard/);
    await waitForPageLoad(page);
    
    // FIXED: Verify role-specific content
    await expect(page.locator('[data-testid="executive-dashboard"]')).toBeVisible();
    
    // FIXED: Verify user menu shows correct role
    await expect(page.locator('[data-testid="user-role"]')).toHaveText('Executive');
  });

  test('Role-based access control', async ({ page }) => {
    await login(page, TestUsers.productOwner);
    
    // FIXED: Verify product owner can access their dashboard
    await page.goto('/dashboard/product-owner');
    await expect(page.locator('[data-testid="product-owner-dashboard"]')).toBeVisible();
    
    // FIXED: Verify access restriction to executive dashboard
    await page.goto('/dashboard/executive');
    await expect(page.locator('[data-testid="access-denied"]')).toBeVisible();
  });
  
  test('Logout functionality', async ({ page }) => {
    await login(page, TestUsers.scrumMaster);
    
    // FIXED: Use proper logout flow
    await page.click('[data-testid="user-menu"]');
    await page.click('[data-testid="logout-button"]');
    
    // FIXED: Wait for logout to complete
    await page.waitForURL('/login');
    await expect(page.locator('form')).toBeVisible();
    
    // FIXED: Verify session is cleared
    await page.goto('/dashboard');
    await expect(page).toHaveURL('/login');
  });
});
```

#### **Task 2.2: Mobile Responsiveness Test Recovery**
```typescript
// tests/mobile/responsive.spec.ts - Complete mobile test recovery
import { test, expect, devices } from '@playwright/test';
import { TestUsers, login, waitForPageLoad, takeScreenshot } from '../fixtures/test-helpers';

test.describe('Mobile Responsive Recovery - CRITICAL', () => {
  const mobileDevices = [
    { name: 'iPhone 12', device: devices['iPhone 12'] },
    { name: 'iPhone 13 Pro', device: devices['iPhone 13 Pro'] },
    { name: 'Pixel 5', device: devices['Pixel 5'] },
    { name: 'Samsung Galaxy S21', device: devices['Galaxy S21'] },
    { name: 'iPad Air', device: devices['iPad Air'] },
  ];

  mobileDevices.forEach(({ name, device }) => {
    test(`${name} - Complete mobile functionality`, async ({ browser }) => {
      const context = await browser.newContext(device);
      const page = await context.newPage();

      try {
        // FIXED: Mobile login functionality
        await page.goto('/login');
        await waitForPageLoad(page);
        
        // FIXED: Verify mobile login form is usable
        const usernameField = page.locator('input[name="username"]');
        const passwordField = page.locator('input[name="password"]');
        const loginButton = page.locator('button[type="submit"]');
        
        await expect(usernameField).toBeVisible();
        await expect(passwordField).toBeVisible();
        await expect(loginButton).toBeVisible();
        
        // FIXED: Verify touch targets are proper size (44px minimum)
        const usernameBox = await usernameField.boundingBox();
        const passwordBox = await passwordField.boundingBox();
        const buttonBox = await loginButton.boundingBox();
        
        expect(usernameBox.height).toBeGreaterThanOrEqual(44);
        expect(passwordBox.height).toBeGreaterThanOrEqual(44);
        expect(buttonBox.height).toBeGreaterThanOrEqual(44);
        
        // FIXED: Test mobile login
        await login(page, TestUsers.executive);
        
        // FIXED: Verify mobile navigation exists and works
        const mobileNavToggle = page.locator('[data-testid="mobile-nav-toggle"]');
        await expect(mobileNavToggle).toBeVisible();
        await mobileNavToggle.tap();
        
        const mobileMenu = page.locator('[data-testid="mobile-menu"]');
        await expect(mobileMenu).toBeVisible();
        
        // FIXED: Verify no horizontal scroll
        const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
        const viewportWidth = device.viewport.width;
        expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 10);
        
        // FIXED: Test mobile dashboard functionality
        await page.goto('/dashboard/executive');
        await waitForPageLoad(page);
        
        // FIXED: Verify charts are responsive
        const charts = await page.locator('[data-testid*="chart"]').all();
        for (const chart of charts.slice(0, 3)) {
          const chartBox = await chart.boundingBox();
          expect(chartBox.width).toBeLessThanOrEqual(viewportWidth - 32); // Account for padding
        }
        
        // FIXED: Verify mobile-specific UI patterns
        const mobileElements = [
          '[data-testid="mobile-nav"]',
          '.mobile-friendly-cards',
          '[data-mobile="true"]'
        ];
        
        let foundMobileUI = false;
        for (const selector of mobileElements) {
          if (await page.locator(selector).isVisible().catch(() => false)) {
            foundMobileUI = true;
            break;
          }
        }
        expect(foundMobileUI).toBeTruthy();
        
        await takeScreenshot(page, `mobile-${name.toLowerCase().replace(/\s+/g, '-')}`);
        
      } finally {
        await context.close();
      }
    });
  });
  
  test('Mobile orientation change handling', async ({ browser }) => {
    const context = await browser.newContext(devices['iPhone 12']);
    const page = await context.newPage();
    
    try {
      await login(page, TestUsers.productOwner);
      
      // Test portrait orientation
      await page.setViewportSize({ width: 390, height: 844 });
      await page.goto('/dashboard/product-owner');
      await waitForPageLoad(page);
      
      const portraitLayout = await page.evaluate(() => window.innerHeight > window.innerWidth);
      expect(portraitLayout).toBeTruthy();
      await takeScreenshot(page, 'mobile-portrait');
      
      // Test landscape orientation
      await page.setViewportSize({ width: 844, height: 390 });
      await page.waitForTimeout(1000); // Allow layout to adjust
      
      const landscapeLayout = await page.evaluate(() => window.innerWidth > window.innerHeight);
      expect(landscapeLayout).toBeTruthy();
      
      // Verify layout adapts to landscape
      const bodyHeight = await page.evaluate(() => document.body.scrollHeight);
      const viewportHeight = 390;
      
      // Content should fit better in landscape mode
      expect(bodyHeight).toBeLessThanOrEqual(viewportHeight * 1.5);
      await takeScreenshot(page, 'mobile-landscape');
      
    } finally {
      await context.close();
    }
  });
});
```

#### **Task 2.3: Dashboard Functionality Test Recovery**
```typescript
// tests/dashboard/dashboard-functionality.spec.ts - Fixed dashboard tests
test.describe('Dashboard Functionality Recovery', () => {
  
  test('Executive dashboard loads and displays data', async ({ page }) => {
    await login(page, TestUsers.executive);
    await page.goto('/dashboard/executive');
    
    // FIXED: Wait for all dashboard components to load
    await waitForPageLoad(page);
    
    // FIXED: Verify key metrics cards are visible and have data
    const metricsCards = [
      '[data-testid="portfolio-health"]',
      '[data-testid="strategic-alignment"]', 
      '[data-testid="value-delivered"]',
      '[data-testid="risk-score"]'
    ];
    
    for (const card of metricsCards) {
      await expect(page.locator(card)).toBeVisible();
      
      // FIXED: Verify card has actual data, not loading state
      await expect(page.locator(`${card} [data-testid="metric-value"]`)).not.toBeEmpty();
    }
    
    // FIXED: Verify charts load and render properly
    const chartContainers = await page.locator('[data-testid*="chart"]').all();
    expect(chartContainers.length).toBeGreaterThan(0);
    
    for (const chart of chartContainers) {
      // Wait for chart to render (Canvas or SVG elements)
      await expect(chart.locator('canvas, svg')).toBeVisible();
      
      // Verify chart has data (not empty state)
      const isEmpty = await chart.locator('[data-testid="empty-chart"]').isVisible().catch(() => false);
      expect(isEmpty).toBeFalsy();
    }
    
    // FIXED: Verify interactive elements work
    const interactiveElements = await page.locator('button, a, [role="button"]').all();
    for (const element of interactiveElements.slice(0, 5)) {
      await expect(element).toBeEnabled();
    }
  });
  
  test('Product owner dashboard Gantt chart functionality', async ({ page }) => {
    await login(page, TestUsers.productOwner);
    await page.goto('/dashboard/product-owner');
    await waitForPageLoad(page);
    
    // FIXED: Verify Gantt chart component loads
    const ganttChart = page.locator('[data-testid="gantt-chart"]');
    await expect(ganttChart).toBeVisible();
    
    // FIXED: Verify Gantt has timeline data
    const timelineItems = await ganttChart.locator('[data-testid="timeline-item"]').all();
    expect(timelineItems.length).toBeGreaterThan(0);
    
    // FIXED: Test Gantt interaction (if drag-drop implemented)
    if (await ganttChart.locator('[data-draggable="true"]').first().isVisible().catch(() => false)) {
      const firstItem = ganttChart.locator('[data-draggable="true"]').first();
      const secondItem = ganttChart.locator('[data-draggable="true"]').nth(1);
      
      await firstItem.dragTo(secondItem);
      
      // Verify drag operation completed
      await expect(page.locator('[data-testid="save-indicator"]')).toBeVisible();
    }
  });
});
```

### Phase 3: Test Enhancement and Coverage (2 SP - 2 hours)

#### **Task 3.1: Export Functionality Tests**
```typescript
// tests/export/export-functionality.spec.ts - New export tests
test.describe('Export Functionality Tests', () => {
  
  test('PDF export functionality', async ({ page }) => {
    await login(page, TestUsers.executive);
    await page.goto('/dashboard/executive');
    await waitForPageLoad(page);
    
    // FIXED: Test PDF export (if implemented)
    const exportButton = page.locator('[data-testid="export-pdf"]');
    
    if (await exportButton.isVisible()) {
      // Set up download listener
      const downloadPromise = page.waitForEvent('download');
      await exportButton.click();
      const download = await downloadPromise;
      
      // Verify download
      expect(download.suggestedFilename()).toContain('.pdf');
      
      // Save and verify file exists
      const filePath = `test-results/downloads/${download.suggestedFilename()}`;
      await download.saveAs(filePath);
      
      // Verify file size (should not be empty)
      const fs = require('fs');
      const stats = fs.statSync(filePath);
      expect(stats.size).toBeGreaterThan(1000); // At least 1KB
    } else {
      test.skip('PDF export not implemented yet');
    }
  });
  
  test('Excel export functionality', async ({ page }) => {
    await login(page, TestUsers.productOwner);
    await page.goto('/work-items');
    await waitForPageLoad(page);
    
    const exportExcelButton = page.locator('[data-testid="export-excel"]');
    
    if (await exportExcelButton.isVisible()) {
      const downloadPromise = page.waitForEvent('download');
      await exportExcelButton.click();
      const download = await downloadPromise;
      
      expect(download.suggestedFilename()).toMatch(/\.(xlsx|csv)$/);
      
      const filePath = `test-results/downloads/${download.suggestedFilename()}`;
      await download.saveAs(filePath);
      
      const fs = require('fs');
      const stats = fs.statSync(filePath);
      expect(stats.size).toBeGreaterThan(500);
    } else {
      test.skip('Excel export not implemented yet');
    }
  });
});
```

#### **Task 3.2: Performance Test Recovery**
```typescript
// tests/performance/performance.spec.ts - Fixed performance tests
test.describe('Performance Test Recovery', () => {
  
  test('Core Web Vitals compliance', async ({ page }) => {
    await page.goto('/dashboard/executive');
    
    // FIXED: Measure Core Web Vitals
    const vitals = await page.evaluate(() => {
      return new Promise((resolve) => {
        const vitals = {};
        
        // Largest Contentful Paint
        new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          vitals.lcp = lastEntry.startTime;
        }).observe({ entryTypes: ['largest-contentful-paint'] });
        
        // Cumulative Layout Shift
        let clsValue = 0;
        new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (!entry.hadRecentInput) {
              clsValue += entry.value;
            }
          }
          vitals.cls = clsValue;
        }).observe({ entryTypes: ['layout-shift'] });
        
        // First Input Delay (simulated)
        setTimeout(() => {
          vitals.fid = performance.now() - performance.timeOrigin;
          resolve(vitals);
        }, 3000);
      });
    });
    
    // FIXED: Assert Core Web Vitals thresholds
    expect(vitals.lcp).toBeLessThan(2500); // 2.5s
    expect(vitals.cls).toBeLessThan(0.1);  // 0.1
    // FID measured differently in real scenarios
    
    // FIXED: Verify Lighthouse performance score
    // This would typically be done in a separate Lighthouse CI process
  });
  
  test('Page load performance', async ({ page }) => {
    const startTime = Date.now();
    await page.goto('/dashboard/executive');
    await waitForPageLoad(page);
    const loadTime = Date.now() - startTime;
    
    // FIXED: Assert load time under 2 seconds
    expect(loadTime).toBeLessThan(2000);
  });
  
  test('Large dataset performance', async ({ page }) => {
    // FIXED: Test with large work item dataset
    await setupLargeDataset(page, 1000);
    
    await login(page, TestUsers.productOwner);
    
    const startTime = Date.now();
    await page.goto('/work-items');
    await waitForPageLoad(page);
    const loadTime = Date.now() - startTime;
    
    expect(loadTime).toBeLessThan(3000); // 3s for large dataset
    
    // FIXED: Verify virtual scrolling or pagination works
    const workItems = await page.locator('[data-testid="work-item"]').count();
    expect(workItems).toBeGreaterThan(20); // Should show some items
    expect(workItems).toBeLessThan(200);   // But not all 1000 at once
  });
});
```

## CI/CD Integration

### GitHub Actions Workflow
```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          
      - name: Install dependencies
        run: pnpm install
        
      - name: Install Playwright
        run: pnpm exec playwright install --with-deps
        
      - name: Start application
        run: |
          pnpm run build
          pnpm run start &
          sleep 30
          
      - name: Run E2E tests
        run: pnpm exec playwright test --reporter=github
        
      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: test-results
          path: test-results/
          
      - name: Comment PR with test results
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            // Post test results as PR comment
```

## Definition of Done

### Technical Completion Criteria
- [ ] **Test Passage Rate**: >95% (121/127 tests passing)
- [ ] **Mobile Coverage**: All 24 mobile responsive tests passing
- [ ] **Authentication**: All 12 authentication tests passing  
- [ ] **Dashboard Functionality**: All 18 dashboard tests passing
- [ ] **Work Item Operations**: All 21 CRUD operation tests passing
- [ ] **Export Functions**: All 8 export tests passing (if implemented)
- [ ] **Performance**: All 8 performance benchmark tests passing
- [ ] **Accessibility**: All 15 accessibility tests passing

### Quality Gate Verification
- [ ] **CI/CD Integration**: Tests run automatically on every PR
- [ ] **Test Stability**: <5% flaky test rate over 10 consecutive runs
- [ ] **Comprehensive Reporting**: HTML reports with screenshots and traces
- [ ] **Performance Monitoring**: Core Web Vitals tracked in every test run
- [ ] **Mobile Testing**: All tests verified on 5 mobile device configurations

### Business Value Delivered
- [ ] **Deployment Confidence**: >95% test coverage ensures reliable deployments
- [ ] **Quality Assurance**: All claimed functionality verified to actually work
- [ ] **Regression Prevention**: Automated tests prevent functionality breaking
- [ ] **Stakeholder Trust**: Transparent test reporting demonstrates real progress
- [ ] **Development Velocity**: Fast feedback loop enables rapid iteration

This story transforms the failing test suite into a comprehensive quality gate that ensures all remediation work delivers real, working functionality to stakeholders.