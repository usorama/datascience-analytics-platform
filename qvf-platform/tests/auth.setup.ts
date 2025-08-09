import { test as setup } from '@playwright/test';
import { TestUsers } from './fixtures/test-users';

/**
 * Authentication setup for QVF Platform E2E tests
 * Pre-authenticates users and saves authentication states
 */

// Authenticate and save state for executive user
setup('authenticate executive', async ({ page, context }) => {
  await page.goto('/login');
  
  // Login as executive
  await page.fill('[data-testid="username"], input[name="username"], input[type="text"]', TestUsers.executive.username);
  await page.fill('[data-testid="password"], input[name="password"], input[type="password"]', TestUsers.executive.password);
  await page.click('[data-testid="login-button"], button[type="submit"], button:has-text("Login"), button:has-text("Sign In")');
  
  // Wait for successful login
  await page.waitForURL('/dashboard/executive', { timeout: 30000 });
  
  // Save authentication state
  await context.storageState({ path: 'test-results/auth/executive.json' });
});

// Authenticate and save state for product owner
setup('authenticate product owner', async ({ page, context }) => {
  await page.goto('/login');
  
  await page.fill('[data-testid="username"], input[name="username"], input[type="text"]', TestUsers.productOwner.username);
  await page.fill('[data-testid="password"], input[name="password"], input[type="password"]', TestUsers.productOwner.password);
  await page.click('[data-testid="login-button"], button[type="submit"], button:has-text("Login"), button:has-text("Sign In")');
  
  // Wait for successful login
  await page.waitForURL('/dashboard/product-owner', { timeout: 30000 });
  
  // Save authentication state
  await context.storageState({ path: 'test-results/auth/product-owner.json' });
});

// Authenticate and save state for scrum master
setup('authenticate scrum master', async ({ page, context }) => {
  await page.goto('/login');
  
  await page.fill('[data-testid="username"], input[name="username"], input[type="text"]', TestUsers.scrumMaster.username);
  await page.fill('[data-testid="password"], input[name="password"], input[type="password"]', TestUsers.scrumMaster.password);
  await page.click('[data-testid="login-button"], button[type="submit"], button:has-text("Login"), button:has-text("Sign In")');
  
  // Wait for successful login
  await page.waitForURL('/dashboard/scrum-master', { timeout: 30000 });
  
  // Save authentication state
  await context.storageState({ path: 'test-results/auth/scrum-master.json' });
});

// Authenticate and save state for developer
setup('authenticate developer', async ({ page, context }) => {
  await page.goto('/login');
  
  await page.fill('[data-testid="username"], input[name="username"], input[type="text"]', TestUsers.developer.username);
  await page.fill('[data-testid="password"], input[name="password"], input[type="password"]', TestUsers.developer.password);
  await page.click('[data-testid="login-button"], button[type="submit"], button:has-text("Login"), button:has-text("Sign In")');
  
  // Wait for successful login - developer lands on general dashboard
  try {
    await page.waitForURL('/dashboard/developer', { timeout: 15000 });
  } catch {
    // Developer may land on general dashboard instead of specific developer dashboard
    try {
      await page.waitForURL('/dashboard', { timeout: 15000 });
    } catch {
      // Final fallback to work-items page
      await page.waitForURL('/work-items', { timeout: 15000 });
    }
  }
  
  // Save authentication state
  await context.storageState({ path: 'test-results/auth/developer.json' });
});