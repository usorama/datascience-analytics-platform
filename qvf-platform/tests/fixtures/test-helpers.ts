import { Page, expect, Locator } from '@playwright/test';
import { TestUser, TestUsers } from './test-users';

/**
 * Helper functions for QVF Platform E2E tests
 */

/**
 * Wait for page to fully load including network requests
 */
export async function waitForPageLoad(page: Page, timeout = 10000): Promise<void> {
  await page.waitForLoadState('networkidle', { timeout });
  await page.waitForTimeout(500); // Additional buffer for animations
}

/**
 * Login helper that works with the QVF authentication system
 */
export async function login(page: Page, user: TestUser): Promise<void> {
  await page.goto('/login');
  await waitForPageLoad(page);

  // Fill login form with robust selectors
  const usernameField = page.locator('[data-testid="username"], input[name="username"], input[type="text"]').first();
  const passwordField = page.locator('[data-testid="password"], input[name="password"], input[type="password"]').first();
  
  await expect(usernameField).toBeVisible({ timeout: 10000 });
  await expect(passwordField).toBeVisible({ timeout: 10000 });
  
  await usernameField.fill(user.username);
  await passwordField.fill(user.password);
  
  // Click login button
  const loginButton = page.locator('[data-testid="login-button"], button[type="submit"], button:has-text("Login"), button:has-text("Sign In")').first();
  await expect(loginButton).toBeVisible({ timeout: 10000 });
  await loginButton.click();
  
  // Wait for successful login and redirect
  try {
    await page.waitForURL(user.defaultRoute, { timeout: 20000 });
  } catch {
    // Fallback: wait for any dashboard or authenticated page
    await page.waitForURL(/\/(dashboard|work-items|compare)/, { timeout: 20000 });
  }
  
  await waitForPageLoad(page);
}

/**
 * Logout helper
 */
export async function logout(page: Page): Promise<void> {
  const logoutSelectors = [
    '[data-testid="logout-button"]',
    '[data-testid="user-menu"] button:has-text("Logout")',
    'button:has-text("Logout")',
    'button:has-text("Sign Out")',
    '[aria-label="Logout"]',
    '.logout-btn'
  ];
  
  let loggedOut = false;
  for (const selector of logoutSelectors) {
    try {
      if (await page.isVisible(selector, { timeout: 2000 })) {
        await page.click(selector);
        await waitForPageLoad(page);
        loggedOut = true;
        break;
      }
    } catch {
      // Continue to next selector
    }
  }
  
  if (!loggedOut) {
    // Force logout by clearing storage and navigating to login
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await page.goto('/login');
  }
  
  await waitForPageLoad(page);
}

/**
 * Navigate to a route and wait for it to load
 */
export async function navigateTo(page: Page, route: string): Promise<void> {
  // Try clicking navigation link first
  const navSelectors = [
    `[data-testid="nav-${route.replace(/\//g, '-')}"]`,
    `a[href="${route}"]`,
    `nav a:has-text("${route.split('/').pop()}")`,
  ];
  
  let navigated = false;
  for (const selector of navSelectors) {
    try {
      if (await page.isVisible(selector, { timeout: 2000 })) {
        await page.click(selector);
        await waitForPageLoad(page);
        navigated = true;
        break;
      }
    } catch {
      // Continue to next selector
    }
  }
  
  if (!navigated) {
    // Direct navigation
    await page.goto(route);
    await waitForPageLoad(page);
  }
}

/**
 * Check if user has access to a route
 */
export async function checkRouteAccess(page: Page, route: string, shouldHaveAccess: boolean): Promise<void> {
  await page.goto(route);
  
  if (shouldHaveAccess) {
    // Should not be redirected to login or error page
    await expect(page).not.toHaveURL(/\/login/);
    await expect(page).not.toHaveURL(/\/403/);
    await expect(page).not.toHaveURL(/\/unauthorized/);
  } else {
    // Should be redirected to login or error page
    await page.waitForURL(/\/(login|403|unauthorized)/, { timeout: 10000 });
  }
}

/**
 * Wait for an element to be visible and stable
 */
export async function waitForElement(page: Page, selector: string, timeout = 10000): Promise<Locator> {
  const element = page.locator(selector);
  await element.waitFor({ state: 'visible', timeout });
  return element;
}

/**
 * Fill form field with error handling
 */
export async function fillField(page: Page, selector: string, value: string): Promise<void> {
  const field = await waitForElement(page, selector);
  await field.clear();
  await field.fill(value);
  
  // Verify the value was set correctly
  await expect(field).toHaveValue(value);
}

/**
 * Take a screenshot with a descriptive name
 */
export async function takeScreenshot(page: Page, name: string, options?: { fullPage?: boolean }): Promise<void> {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  await page.screenshot({
    path: `test-results/screenshots/${timestamp}-${name}.png`,
    fullPage: options?.fullPage || true,
  });
}

/**
 * Check if element contains expected text
 */
export async function expectElementToContainText(page: Page, selector: string, expectedText: string): Promise<void> {
  const element = await waitForElement(page, selector);
  await expect(element).toContainText(expectedText);
}

/**
 * Check API response time
 */
export async function checkAPIResponseTime(page: Page, apiEndpoint: string, maxResponseTime = 2000): Promise<void> {
  const startTime = Date.now();
  
  await page.route(apiEndpoint, async (route) => {
    const response = await route.fetch();
    const endTime = Date.now();
    const responseTime = endTime - startTime;
    
    expect(responseTime).toBeLessThan(maxResponseTime);
    await route.fulfill({ response });
  });
}

/**
 * Mock API response for testing
 */
export async function mockAPIResponse(page: Page, apiEndpoint: string, mockData: any): Promise<void> {
  await page.route(apiEndpoint, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockData),
    });
  });
}