import { defineConfig, devices } from '@playwright/test';

/**
 * QVF Platform Playwright E2E Test Configuration
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './tests',
  
  /* Global test configuration */
  fullyParallel: !process.env.CI, // Parallel locally, sequential on CI for stability
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 1, // More retries on CI for flaky network issues
  workers: process.env.CI ? 2 : 4, // Controlled parallelism
  timeout: 60000, // 60 seconds for complex E2E tests
  expect: { timeout: 15000 }, // 15 seconds for assertions
  
  /* Reporters */
  reporter: [
    ['html', { outputFolder: 'test-results/html-report', open: 'never' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/results.xml' }],
    process.env.CI ? ['github'] : ['list'],
  ],
  
  /* Output configuration */
  outputDir: 'test-results/artifacts',
  
  /* Global test options */
  use: {
    /* Base URL configurations */
    baseURL: process.env.BASE_URL || 'http://localhost:3006',
    
    /* Browser context options */
    viewport: { width: 1440, height: 900 },
    ignoreHTTPSErrors: true,
    
    /* Screenshots and videos */
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    
    /* Tracing */
    trace: process.env.CI ? 'on-first-retry' : 'retain-on-failure',
    
    /* Navigation timeout */
    navigationTimeout: 30000,
    actionTimeout: 15000,
  },

  /* Environment-specific configurations */
  projects: [
    // Setup project for authentication
    {
      name: 'setup',
      testMatch: /.*\.setup\.ts/,
      teardown: 'cleanup',
    },
    
    // Cleanup project
    {
      name: 'cleanup',
      testMatch: /.*\.cleanup\.ts/,
    },

    /* Desktop browsers */
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        contextOptions: {
          permissions: ['clipboard-read', 'clipboard-write'],
        },
      },
      dependencies: ['setup'],
    },
    
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
      dependencies: ['setup'],
    },
    
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
      dependencies: ['setup'],
    },

    /* Mobile testing */
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
      dependencies: ['setup'],
      testIgnore: [
        '**/performance.spec.ts', // Skip performance tests on mobile
      ],
    },
    
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 12'] },
      dependencies: ['setup'],
      testIgnore: [
        '**/performance.spec.ts', // Skip performance tests on mobile
      ],
    },

    /* Tablet testing */
    {
      name: 'tablet',
      use: { ...devices['iPad Pro'] },
      dependencies: ['setup'],
    },

    /* API testing project */
    {
      name: 'api',
      testMatch: '**/api/*.spec.ts',
      use: {
        baseURL: process.env.API_BASE_URL || 'http://localhost:8000',
      },
    },

    /* Performance testing */
    {
      name: 'performance',
      testMatch: '**/performance/*.spec.ts',
      use: { ...devices['Desktop Chrome'] },
      dependencies: ['setup'],
      retries: 0, // No retries for performance tests
    },

    /* Visual regression testing */
    {
      name: 'visual',
      testMatch: '**/visual/*.spec.ts',
      use: { 
        ...devices['Desktop Chrome'],
        screenshot: 'only-on-failure',
      },
      dependencies: ['setup'],
    },
  ],

  /* Web servers for local development */
  webServer: [
    {
      command: 'pnpm run dev:web',
      url: 'http://localhost:3006',
      reuseExistingServer: !process.env.CI,
      timeout: 120000,
      env: {
        NODE_ENV: 'test',
      },
    },
    {
      command: 'pnpm run dev:api',
      url: 'http://localhost:8000/health',
      reuseExistingServer: !process.env.CI,
      timeout: 60000,
    },
  ],

  /* Global setup and teardown */
  globalSetup: require.resolve('./tests/global-setup.ts'),
  globalTeardown: require.resolve('./tests/global-teardown.ts'),
});