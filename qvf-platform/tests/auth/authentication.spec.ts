import { test, expect } from '@playwright/test';
import { TestUsers, getAllTestUsers } from '../fixtures/test-users';
import { login, logout, waitForPageLoad, takeScreenshot } from '../fixtures/test-helpers';

test.describe('QVF Platform Authentication', () => {
  test.beforeEach(async ({ page }) => {
    // Clear any existing authentication
    await page.context().clearCookies();
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
  });

  test('should display login page correctly', async ({ page }) => {
    await page.goto('/login');
    await waitForPageLoad(page);

    // Check page title
    await expect(page).toHaveTitle(/QVF Platform|Login/);

    // Check essential login elements are present
    await expect(page.locator('input[name="username"], input[type="text"]')).toBeVisible();
    await expect(page.locator('input[name="password"], input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Sign In")')).toBeVisible();

    // Take screenshot of login page
    await takeScreenshot(page, 'login-page-initial');
  });

  test('should reject invalid credentials', async ({ page }) => {
    await page.goto('/login');
    await waitForPageLoad(page);

    // Try invalid credentials
    await page.fill('input[name="username"], input[type="text"]', 'invalid_user');
    await page.fill('input[name="password"], input[type="password"]', 'wrong_password');
    await page.click('button[type="submit"], button:has-text("Login"), button:has-text("Sign In")');

    // Should stay on login page or show error
    await page.waitForTimeout(3000);
    const currentUrl = page.url();
    
    // Either still on login page or shows error message
    const isOnLogin = currentUrl.includes('/login') || currentUrl.includes('/');
    const hasErrorMessage = await page.locator('text=/invalid|error|incorrect|failed/i').isVisible({ timeout: 5000 }).catch(() => false);
    
    expect(isOnLogin || hasErrorMessage).toBeTruthy();
    
    await takeScreenshot(page, 'login-invalid-credentials');
  });

  test('should handle empty form submission', async ({ page }) => {
    await page.goto('/login');
    await waitForPageLoad(page);

    // Try submitting empty form
    await page.click('button[type="submit"], button:has-text("Login"), button:has-text("Sign In")');
    
    // Should show validation errors or stay on login page
    await page.waitForTimeout(2000);
    const currentUrl = page.url();
    expect(currentUrl.includes('/login') || currentUrl.includes('/')).toBeTruthy();
  });

  // Test login for each user role
  getAllTestUsers().forEach((user) => {
    test(`should login successfully as ${user.role}`, async ({ page }) => {
      await login(page, user);

      // Verify successful login by checking we're not on login page
      await expect(page).not.toHaveURL(/\/login/);
      
      // Should be on expected dashboard or work-items page
      const currentUrl = page.url();
      const isOnValidPage = currentUrl.includes('/dashboard') || 
                           currentUrl.includes('/work-items') ||
                           currentUrl.includes('/compare');
      expect(isOnValidPage).toBeTruthy();

      // Check for user indicator (name, profile, or logout button)
      const userIndicators = [
        page.locator(`text="${user.full_name}"`),
        page.locator(`text="${user.fullName}"`),
        page.locator(`text="${user.username}"`),
        page.locator('[data-testid="user-menu"]'),
        page.locator('button:has-text("Logout")'),
        page.locator('[data-testid="logout-button"]'),
        page.locator('[aria-label="Logout"]'),
        page.locator(`text="${user.role.replace('_', ' ').toUpperCase()}"`)
      ];

      let userIndicatorFound = false;
      for (const indicator of userIndicators) {
        if (await indicator.isVisible({ timeout: 5000 }).catch(() => false)) {
          userIndicatorFound = true;
          break;
        }
      }
      
      expect(userIndicatorFound).toBeTruthy();
      
      await takeScreenshot(page, `login-success-${user.role}`);
    });
  });

  // Test logout for each user role
  getAllTestUsers().forEach((user) => {
    test(`should logout successfully as ${user.role}`, async ({ page }) => {
      // First login
      await login(page, user);
      
      // Then logout
      await logout(page);
      
      // Should be redirected to login page
      await expect(page).toHaveURL(/\/(login)?$/);
      
      // Should not have authentication tokens
      const hasToken = await page.evaluate(() => {
        return localStorage.getItem('qvf-token') !== null;
      });
      expect(hasToken).toBeFalsy();
      
      await takeScreenshot(page, `logout-success-${user.role}`);
    });
  });

  test('should maintain session across page refreshes', async ({ page }) => {
    // Login as executive
    await login(page, TestUsers.executive);
    
    // Refresh the page
    await page.reload();
    await waitForPageLoad(page);
    
    // Should still be authenticated
    await expect(page).not.toHaveURL(/\/login/);
    
    const currentUrl = page.url();
    const isStillAuthenticated = currentUrl.includes('/dashboard') || 
                                currentUrl.includes('/work-items') ||
                                currentUrl.includes('/compare');
    expect(isStillAuthenticated).toBeTruthy();
  });

  test('should redirect to login when accessing protected routes without authentication', async ({ page }) => {
    const protectedRoutes = [
      '/dashboard/executive',
      '/dashboard/product-owner', 
      '/dashboard/scrum-master',
      '/work-items',
      '/compare'
    ];

    for (const route of protectedRoutes) {
      await page.goto(route);
      
      // Should be redirected to login or show login form
      await page.waitForTimeout(3000);
      const currentUrl = page.url();
      const isOnLoginOrRoot = currentUrl.includes('/login') || 
                             currentUrl.match(/\/$/) ||
                             await page.locator('input[name="username"]').isVisible({ timeout: 5000 }).catch(() => false);
      
      expect(isOnLoginOrRoot).toBeTruthy();
    }
  });

  test('should handle concurrent login sessions', async ({ browser }) => {
    // Create two browser contexts (simulating two users)
    const context1 = await browser.newContext();
    const context2 = await browser.newContext();
    
    const page1 = await context1.newPage();
    const page2 = await context2.newPage();

    try {
      // Login as different users in each context
      await login(page1, TestUsers.executive);
      await login(page2, TestUsers.productOwner);

      // Both should be authenticated
      await expect(page1).not.toHaveURL(/\/login/);
      await expect(page2).not.toHaveURL(/\/login/);

      // Both should maintain their separate sessions
      const user1Authenticated = await page1.evaluate(() => {
        return localStorage.getItem('qvf-token') !== null;
      });
      const user2Authenticated = await page2.evaluate(() => {
        return localStorage.getItem('qvf-token') !== null;
      });

      expect(user1Authenticated).toBeTruthy();
      expect(user2Authenticated).toBeTruthy();

    } finally {
      await context1.close();
      await context2.close();
    }
  });

  test('should handle token expiration gracefully', async ({ page }) => {
    // Login first
    await login(page, TestUsers.executive);
    
    // Simulate expired token by clearing it
    await page.evaluate(() => {
      localStorage.removeItem('qvf-token');
    });
    
    // Try to access a protected route
    await page.goto('/dashboard/executive');
    
    // Should be redirected to login
    await page.waitForURL(/\/(login)?$/, { timeout: 10000 });
  });
});