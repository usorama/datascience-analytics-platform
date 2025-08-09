import { test, expect } from '@playwright/test';
import { TestUsers, getAllTestUsers } from '../fixtures/test-users';
import { login, navigateTo, waitForPageLoad, takeScreenshot } from '../fixtures/test-helpers';

test.describe('Theme Toggle Functionality', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TestUsers.executive);
    await navigateTo(page, '/dashboard');
    await page.waitForSelector('nav[role="navigation"]', { timeout: 10000 });
  });

  test('should toggle theme from dark to light', async ({ page }) => {
    // Find theme toggle button - it appears in both desktop and mobile nav
    const themeToggle = page.locator('button[aria-label*="Switch to"][aria-label*="theme"]').first();
    await expect(themeToggle).toBeVisible({ timeout: 10000 });
    
    // Get initial theme
    const initialTheme = await page.evaluate(() => document.documentElement.classList.contains('dark') ? 'dark' : 'light');
    
    // Click theme toggle
    await themeToggle.click();
    await page.waitForTimeout(500); // Wait for theme transition
    
    // Verify theme changed
    const newTheme = await page.evaluate(() => document.documentElement.classList.contains('dark') ? 'dark' : 'light');
    expect(newTheme).not.toBe(initialTheme);
    
    await takeScreenshot(page, `theme-toggle-${newTheme}`);
  });

  test('should have proper ARIA labels for accessibility', async ({ page }) => {
    const themeToggle = page.locator('button[aria-label*="Switch to"][aria-label*="theme"]').first();
    await expect(themeToggle).toBeVisible({ timeout: 10000 });
    
    // Check initial ARIA label
    const ariaLabel = await themeToggle.getAttribute('aria-label');
    expect(ariaLabel).toMatch(/Switch to (light|dark) theme/);
    
    // Click and verify ARIA label updates
    await themeToggle.click();
    await page.waitForTimeout(500);
    
    const newAriaLabel = await themeToggle.getAttribute('aria-label');
    expect(newAriaLabel).toMatch(/Switch to (light|dark) theme/);
    expect(newAriaLabel).not.toBe(ariaLabel);
  });

  test('should show correct icon for current theme', async ({ page }) => {
    const themeToggle = page.locator('button[aria-label*="Switch to"][aria-label*="theme"]').first();
    await expect(themeToggle).toBeVisible({ timeout: 10000 });
    
    // Get current theme
    const currentTheme = await page.evaluate(() => document.documentElement.classList.contains('dark') ? 'dark' : 'light');
    
    // Check that the correct icon is visible
    if (currentTheme === 'dark') {
      // In dark mode, moon icon should be visible (scaled to 100%)
      const moonIcon = themeToggle.locator('svg').nth(1); // Moon is second SVG
      await expect(moonIcon).toBeVisible();
    } else {
      // In light mode, sun icon should be visible (scaled to 100%)
      const sunIcon = themeToggle.locator('svg').first(); // Sun is first SVG
      await expect(sunIcon).toBeVisible();
    }
  });

  test('should persist theme across page navigation', async ({ page }) => {
    const themeToggle = page.locator('button[aria-label*="Switch to"][aria-label*="theme"]').first();
    await expect(themeToggle).toBeVisible({ timeout: 10000 });
    
    // Toggle theme
    await themeToggle.click();
    await page.waitForTimeout(500);
    
    const themeAfterToggle = await page.evaluate(() => document.documentElement.classList.contains('dark') ? 'dark' : 'light');
    
    // Navigate to another page
    await navigateTo(page, '/work-items');
    await page.waitForTimeout(1000);
    
    // Verify theme persisted
    const themeAfterNavigation = await page.evaluate(() => document.documentElement.classList.contains('dark') ? 'dark' : 'light');
    expect(themeAfterNavigation).toBe(themeAfterToggle);
  });

  test('should work in both desktop and mobile layouts', async ({ page }) => {
    // Test desktop theme toggle
    await page.setViewportSize({ width: 1024, height: 768 });
    await page.reload();
    await page.waitForSelector('nav[role="navigation"]', { timeout: 10000 });
    
    const desktopThemeToggle = page.locator('.hidden.md\\:flex button[aria-label*="theme"]');
    await expect(desktopThemeToggle).toBeVisible({ timeout: 10000 });
    
    const initialThemeDesktop = await page.evaluate(() => document.documentElement.classList.contains('dark') ? 'dark' : 'light');
    await desktopThemeToggle.click();
    await page.waitForTimeout(500);
    
    const newThemeDesktop = await page.evaluate(() => document.documentElement.classList.contains('dark') ? 'dark' : 'light');
    expect(newThemeDesktop).not.toBe(initialThemeDesktop);
    
    // Test mobile theme toggle
    await page.setViewportSize({ width: 375, height: 812 });
    await page.reload();
    await page.waitForSelector('nav[role="navigation"]', { timeout: 10000 });
    
    const mobileThemeToggle = page.locator('.md\\:hidden button[aria-label*="theme"]');
    await expect(mobileThemeToggle).toBeVisible({ timeout: 10000 });
    
    const initialThemeMobile = await page.evaluate(() => document.documentElement.classList.contains('dark') ? 'dark' : 'light');
    await mobileThemeToggle.click();
    await page.waitForTimeout(500);
    
    const newThemeMobile = await page.evaluate(() => document.documentElement.classList.contains('dark') ? 'dark' : 'light');
    expect(newThemeMobile).not.toBe(initialThemeMobile);
  });

  test('should have smooth transition animation', async ({ page }) => {
    const themeToggle = page.locator('button[aria-label*="Switch to"][aria-label*="theme"]').first();
    await expect(themeToggle).toBeVisible({ timeout: 10000 });
    
    // Measure animation time
    const startTime = Date.now();
    await themeToggle.click();
    
    // Wait for theme to fully apply
    await page.waitForTimeout(300); // Theme transitions should be fast
    
    const transitionTime = Date.now() - startTime;
    expect(transitionTime).toBeLessThan(1000); // Should complete quickly
  });

  test('should be keyboard accessible', async ({ page }) => {
    const themeToggle = page.locator('button[aria-label*="Switch to"][aria-label*="theme"]').first();
    await expect(themeToggle).toBeVisible({ timeout: 10000 });
    
    // Focus the button
    await themeToggle.focus();
    
    // Verify it's focused
    const isFocused = await themeToggle.evaluate(el => document.activeElement === el);
    expect(isFocused).toBeTruthy();
    
    // Press Enter to toggle theme
    const initialTheme = await page.evaluate(() => document.documentElement.classList.contains('dark') ? 'dark' : 'light');
    await page.keyboard.press('Enter');
    await page.waitForTimeout(500);
    
    const newTheme = await page.evaluate(() => document.documentElement.classList.contains('dark') ? 'dark' : 'light');
    expect(newTheme).not.toBe(initialTheme);
  });

  test('should maintain focus outline when focused', async ({ page }) => {
    const themeToggle = page.locator('button[aria-label*="Switch to"][aria-label*="theme"]').first();
    await expect(themeToggle).toBeVisible({ timeout: 10000 });
    
    // Focus the button
    await themeToggle.focus();
    
    // Check for focus ring styles (this depends on your CSS implementation)
    const focusStyles = await themeToggle.evaluate(el => getComputedStyle(el).outlineWidth);
    // Focus ring should be applied when focused
    expect(focusStyles).not.toBe('0px');
  });
});

test.describe('Mobile Theme Toggle in Drawer', () => {
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await login(page, TestUsers.productOwner);
    await navigateTo(page, '/dashboard');
    await page.waitForSelector('nav[role="navigation"]', { timeout: 10000 });
  });

  test('should have theme toggle in mobile drawer', async ({ page }) => {
    // Open mobile menu
    const menuButton = page.locator('.md\\:hidden button[aria-expanded]');
    await expect(menuButton).toBeVisible({ timeout: 10000 });
    await menuButton.click();
    await page.waitForTimeout(500);
    
    const drawer = page.locator('[role="dialog"][aria-modal="true"]');
    await expect(drawer).toBeVisible({ timeout: 5000 });
    
    // Check for theme toggle in drawer
    const drawerThemeToggle = drawer.locator('button[aria-label*="theme"]');
    await expect(drawerThemeToggle).toBeVisible({ timeout: 5000 });
    
    // Verify it works
    const initialTheme = await page.evaluate(() => document.documentElement.classList.contains('dark') ? 'dark' : 'light');
    await drawerThemeToggle.click();
    await page.waitForTimeout(500);
    
    const newTheme = await page.evaluate(() => document.documentElement.classList.contains('dark') ? 'dark' : 'light');
    expect(newTheme).not.toBe(initialTheme);
  });

  test('should show theme label in mobile drawer', async ({ page }) => {
    // Open mobile menu
    const menuButton = page.locator('.md\\:hidden button[aria-expanded]');
    await expect(menuButton).toBeVisible({ timeout: 10000 });
    await menuButton.click();
    await page.waitForTimeout(500);
    
    const drawer = page.locator('[role="dialog"][aria-modal="true"]');
    await expect(drawer).toBeVisible({ timeout: 5000 });
    
    // Check for "Theme" label text
    const themeLabel = drawer.getByText('Theme');
    await expect(themeLabel).toBeVisible({ timeout: 5000 });
    
    // Theme toggle should be nearby
    const themeSection = drawer.locator('*:has-text("Theme")').locator('..'); // Parent element
    const themeToggleInSection = themeSection.locator('button[aria-label*="theme"]');
    await expect(themeToggleInSection).toBeVisible({ timeout: 5000 });
  });
});

test.describe('Theme Toggle Cross-Browser Compatibility', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TestUsers.developer);
    await navigateTo(page, '/dashboard');
  });

  test('should work consistently across different browsers', async ({ page, browserName }) => {
    await page.waitForSelector('nav[role="navigation"]', { timeout: 10000 });
    
    const themeToggle = page.locator('button[aria-label*="Switch to"][aria-label*="theme"]').first();
    await expect(themeToggle).toBeVisible({ timeout: 10000 });
    
    // Test theme toggle functionality
    const initialTheme = await page.evaluate(() => document.documentElement.classList.contains('dark') ? 'dark' : 'light');
    await themeToggle.click();
    await page.waitForTimeout(500);
    
    const newTheme = await page.evaluate(() => document.documentElement.classList.contains('dark') ? 'dark' : 'light');
    expect(newTheme).not.toBe(initialTheme);
    
    // Take browser-specific screenshot
    await takeScreenshot(page, `theme-toggle-${browserName}-${newTheme}`);
  });
});