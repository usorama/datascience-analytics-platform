import { test, expect, devices } from '@playwright/test';
import { TestUsers, getAllTestUsers } from '../fixtures/test-users';
import { login, navigateTo, waitForPageLoad, takeScreenshot } from '../fixtures/test-helpers';

// Mobile viewport sizes to test
const mobileViewports = [
  { name: 'iPhone SE', ...devices['iPhone SE'] },
  { name: 'iPhone 12', ...devices['iPhone 12'] },
  { name: 'Samsung Galaxy S21', width: 412, height: 915 },
  { name: 'iPad', ...devices['iPad'] },
];

test.describe('Mobile Navigation', () => {
  
  mobileViewports.forEach(({ name, ...viewport }) => {
    test.describe(`${name} Navigation`, () => {
      test.beforeEach(async ({ page, context }) => {
        await context.setViewportSize({ 
          width: viewport.viewport?.width || viewport.width || 375, 
          height: viewport.viewport?.height || viewport.height || 812 
        });
        await login(page, TestUsers.executive);
      });

      test('should display hamburger menu button', async ({ page }) => {
        await navigateTo(page, '/dashboard');
        
        // Wait for navigation to load
        await page.waitForSelector('nav[role="navigation"]', { timeout: 10000 });
        
        // Should show mobile menu button - more specific selector
        const menuButton = page.locator('.md\\:hidden button[aria-label*="menu"]');
        await expect(menuButton).toBeVisible({ timeout: 10000 });
        
        // Should be touch-friendly (44px minimum)
        const buttonSize = await menuButton.boundingBox();
        expect(buttonSize?.width).toBeGreaterThanOrEqual(44);
        expect(buttonSize?.height).toBeGreaterThanOrEqual(44);
        
        await takeScreenshot(page, `mobile-header-${name.toLowerCase().replace(' ', '-')}`);
      });

      test('should open and close mobile navigation drawer', async ({ page }) => {
        await navigateTo(page, '/dashboard');
        await page.waitForSelector('nav[role="navigation"]', { timeout: 10000 });
        
        // Open mobile menu - find button in mobile area
        const menuButton = page.locator('.md\\:hidden button[aria-expanded]');
        await expect(menuButton).toBeVisible({ timeout: 10000 });
        await menuButton.click();
        
        // Wait for drawer animation to complete
        await page.waitForTimeout(500);
        
        // Should show drawer
        const drawer = page.locator('[role="dialog"][aria-modal="true"]');
        await expect(drawer).toBeVisible({ timeout: 10000 });
        
        // Should show navigation items in drawer
        const navItems = drawer.locator('nav[aria-label*="Mobile"] a');
        await expect(navItems.first()).toBeVisible({ timeout: 5000 });
        const itemCount = await navItems.count();
        expect(itemCount).toBeGreaterThan(0);
        
        await takeScreenshot(page, `mobile-drawer-open-${name.toLowerCase().replace(' ', '-')}`);
        
        // Close with X button - look inside drawer
        const closeButton = drawer.locator('button[aria-label*="Close menu"]');
        await expect(closeButton).toBeVisible({ timeout: 5000 });
        await closeButton.click();
        
        // Wait for drawer to close
        await expect(drawer).not.toBeVisible({ timeout: 5000 });
      });

      test('should close drawer when clicking backdrop', async ({ page }) => {
        await navigateTo(page, '/dashboard');
        await page.waitForSelector('nav[role="navigation"]', { timeout: 10000 });
        
        // Open mobile menu
        const menuButton = page.locator('.md\\:hidden button[aria-expanded]');
        await expect(menuButton).toBeVisible({ timeout: 10000 });
        await menuButton.click();
        await page.waitForTimeout(500);
        
        // Should show backdrop - fixed selector for CSS escape
        const backdrop = page.locator('.fixed.inset-0').first();
        await expect(backdrop).toBeVisible({ timeout: 5000 });
        
        // Click backdrop to close (click center to avoid edge issues)
        await backdrop.click({ position: { x: 100, y: 100 } });
        await page.waitForTimeout(300);
        
        // Drawer should close
        const drawer = page.locator('[role="dialog"][aria-modal="true"]');
        await expect(drawer).not.toBeVisible({ timeout: 5000 });
      });

      test('should have touch-friendly navigation targets', async ({ page }) => {
        await navigateTo(page, '/dashboard');
        await page.waitForSelector('nav[role="navigation"]', { timeout: 10000 });
        
        // Open mobile menu
        const menuButton = page.locator('.md\\:hidden button[aria-expanded]');
        await expect(menuButton).toBeVisible({ timeout: 10000 });
        await menuButton.click();
        await page.waitForTimeout(500);
        
        const drawer = page.locator('[role="dialog"][aria-modal="true"]');
        await expect(drawer).toBeVisible({ timeout: 5000 });
        
        const navLinks = drawer.locator('nav[aria-label*="Mobile"] a');
        await expect(navLinks.first()).toBeVisible({ timeout: 5000 });
        
        // Check each navigation item is touch-friendly
        const linkCount = await navLinks.count();
        expect(linkCount).toBeGreaterThan(0);
        
        for (let i = 0; i < Math.min(linkCount, 5); i++) { // Limit check to first 5 items
          const link = navLinks.nth(i);
          await expect(link).toBeVisible({ timeout: 2000 });
          const linkBox = await link.boundingBox();
          
          if (linkBox) {
            expect(linkBox.height).toBeGreaterThanOrEqual(44);
          }
        }
      });

      test('should close drawer when navigating', async ({ page }) => {
        await navigateTo(page, '/dashboard');
        await page.waitForSelector('nav[role="navigation"]', { timeout: 10000 });
        
        // Open mobile menu
        const menuButton = page.locator('.md\\:hidden button[aria-expanded]');
        await expect(menuButton).toBeVisible({ timeout: 10000 });
        await menuButton.click();
        await page.waitForTimeout(500);
        
        const drawer = page.locator('[role="dialog"][aria-modal="true"]');
        await expect(drawer).toBeVisible({ timeout: 5000 });
        
        // Click on a navigation item - look for Work Items link
        const workItemsLink = drawer.locator('nav a').filter({ hasText: 'Work Items' });
        await expect(workItemsLink).toBeVisible({ timeout: 5000 });
        
        await workItemsLink.click();
        
        // Wait for navigation
        await waitForPageLoad(page);
        
        // Drawer should auto-close after navigation
        await expect(drawer).not.toBeVisible({ timeout: 5000 });
        
        // Should be on work items page
        await expect(page).toHaveURL(/\/work-items/, { timeout: 10000 });
      });

      test('should support keyboard navigation', async ({ page }) => {
        await navigateTo(page, '/dashboard');
        await page.waitForSelector('nav[role="navigation"]', { timeout: 10000 });
        
        // Focus on menu button specifically
        const menuButton = page.locator('.md\\:hidden button[aria-expanded]');
        await expect(menuButton).toBeVisible({ timeout: 10000 });
        await menuButton.focus();
        
        // Open mobile menu with keyboard
        await page.keyboard.press('Enter');
        await page.waitForTimeout(500);
        
        const drawer = page.locator('[role="dialog"][aria-modal="true"]');
        await expect(drawer).toBeVisible({ timeout: 5000 });
        
        // Should be able to close with Escape
        await page.keyboard.press('Escape');
        await expect(drawer).not.toBeVisible({ timeout: 5000 });
      });

      test('should prevent body scroll when drawer is open', async ({ page }) => {
        await navigateTo(page, '/dashboard');
        await page.waitForSelector('nav[role="navigation"]', { timeout: 10000 });
        
        // Check initial body overflow (might be empty string or 'auto')
        const initialOverflow = await page.evaluate(() => document.body.style.overflow);
        
        // Open mobile menu
        const menuButton = page.locator('.md\\:hidden button[aria-expanded]');
        await expect(menuButton).toBeVisible({ timeout: 10000 });
        await menuButton.click();
        await page.waitForTimeout(500);
        
        // Body should prevent scroll
        const openOverflow = await page.evaluate(() => document.body.style.overflow);
        expect(openOverflow).toBe('hidden');
        
        // Close menu
        const drawer = page.locator('[role="dialog"][aria-modal="true"]');
        const closeButton = drawer.locator('button[aria-label*="Close menu"]');
        await expect(closeButton).toBeVisible({ timeout: 5000 });
        await closeButton.click();
        
        // Body should restore scroll
        await page.waitForTimeout(300); // Wait for cleanup
        const closedOverflow = await page.evaluate(() => document.body.style.overflow);
        expect(closedOverflow).toBe('auto');
      });

      test('should show user information in drawer', async ({ page }) => {
        await navigateTo(page, '/dashboard');
        await page.waitForSelector('nav[role="navigation"]', { timeout: 10000 });
        
        // Open mobile menu
        const menuButton = page.locator('.md\\:hidden button[aria-expanded]');
        await expect(menuButton).toBeVisible({ timeout: 10000 });
        await menuButton.click();
        await page.waitForTimeout(500);
        
        const drawer = page.locator('[role="dialog"][aria-modal="true"]');
        await expect(drawer).toBeVisible({ timeout: 5000 });
        
        // Should show user name - use contains for more flexible matching
        const userName = drawer.getByText(TestUsers.executive.full_name);
        await expect(userName).toBeVisible({ timeout: 5000 });
        
        // Should show user role - check for formatted role text
        const userRole = drawer.getByText('EXECUTIVE');
        await expect(userRole).toBeVisible({ timeout: 5000 });
        
        // Should show settings and logout buttons - use more flexible selectors
        const settingsButton = drawer.locator('button').filter({ hasText: 'Settings' });
        const logoutButton = drawer.locator('button').filter({ hasText: 'Logout' });
        
        await expect(settingsButton).toBeVisible({ timeout: 5000 });
        await expect(logoutButton).toBeVisible({ timeout: 5000 });
      });
    });
  });

  test.describe('Mobile Responsive Layout', () => {
    test.beforeEach(async ({ page }) => {
      await login(page, TestUsers.productOwner);
    });

    test('should hide desktop navigation on mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 812 }); // iPhone size
      await navigateTo(page, '/dashboard');
      await page.waitForSelector('nav[role="navigation"]', { timeout: 10000 });
      
      // Desktop navigation should be hidden - check specific desktop nav section
      const desktopNav = page.locator('.hidden.md\\:flex').first();
      await expect(desktopNav).not.toBeVisible({ timeout: 5000 });
      
      // Mobile menu button should be visible
      const mobileMenuButton = page.locator('.md\\:hidden button[aria-expanded]');
      await expect(mobileMenuButton).toBeVisible({ timeout: 10000 });
    });

    test('should show desktop navigation on larger screens', async ({ page }) => {
      await page.setViewportSize({ width: 1024, height: 768 }); // Desktop size
      await navigateTo(page, '/dashboard');
      await page.waitForSelector('nav[role="navigation"]', { timeout: 10000 });
      
      // Desktop navigation should be visible
      const desktopNav = page.locator('.hidden.md\\:flex').first();
      await expect(desktopNav).toBeVisible({ timeout: 10000 });
      
      // Mobile menu button should be hidden (it's inside .md:hidden container)
      const mobileMenuButton = page.locator('.md\\:hidden button[aria-expanded]');
      await expect(mobileMenuButton).not.toBeVisible({ timeout: 5000 });
    });

    test('should adapt user info display by screen size', async ({ page }) => {
      // Test mobile layout
      await page.setViewportSize({ width: 375, height: 812 });
      await navigateTo(page, '/dashboard');
      await page.waitForSelector('nav[role="navigation"]', { timeout: 10000 });
      
      // Full user name should be hidden on mobile header (desktop user area is hidden)
      const desktopUserArea = page.locator('.hidden.md\\:flex').last(); // User actions area
      await expect(desktopUserArea).not.toBeVisible({ timeout: 5000 });
      
      // Test desktop layout
      await page.setViewportSize({ width: 1024, height: 768 });
      await page.reload();
      await page.waitForSelector('nav[role="navigation"]', { timeout: 10000 });
      
      // User name should be visible on desktop
      const desktopUserName = page.locator('.hidden.lg\\:inline').filter({ hasText: TestUsers.productOwner.full_name });
      await expect(desktopUserName).toBeVisible({ timeout: 10000 });
    });
  });

  test.describe('Mobile Navigation Accessibility', () => {
    test.beforeEach(async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 812 });
      await login(page, TestUsers.scrumMaster);
    });

    test('should have proper ARIA attributes', async ({ page }) => {
      await navigateTo(page, '/dashboard');
      await page.waitForSelector('nav[role="navigation"]', { timeout: 10000 });
      
      // Menu button should have proper ARIA
      const menuButton = page.locator('.md\\:hidden button[aria-expanded]');
      await expect(menuButton).toBeVisible({ timeout: 10000 });
      await expect(menuButton).toHaveAttribute('aria-expanded', 'false');
      
      // Open menu
      await menuButton.click();
      await page.waitForTimeout(500);
      
      // Button should update ARIA
      await expect(menuButton).toHaveAttribute('aria-expanded', 'true');
      
      // Drawer should have proper role and ARIA
      const drawer = page.locator('[role="dialog"][aria-modal="true"]');
      await expect(drawer).toBeVisible({ timeout: 5000 });
      await expect(drawer).toHaveAttribute('aria-label');
    });

    test('should manage focus properly', async ({ page }) => {
      await navigateTo(page, '/dashboard');
      await page.waitForSelector('nav[role="navigation"]', { timeout: 10000 });
      
      // Focus on menu button and open it
      const menuButton = page.locator('.md\\:hidden button[aria-expanded]');
      await expect(menuButton).toBeVisible({ timeout: 10000 });
      await menuButton.focus();
      await page.keyboard.press('Enter');
      await page.waitForTimeout(500);
      
      const drawer = page.locator('[role="dialog"][aria-modal="true"]');
      await expect(drawer).toBeVisible({ timeout: 5000 });
      
      // Check that focus is managed (drawer should be focusable or contain focusable elements)
      const focusableInDrawer = drawer.locator('button, a, [tabindex="0"]').first();
      await expect(focusableInDrawer).toBeVisible({ timeout: 5000 });
    });

    test('should support screen reader navigation', async ({ page }) => {
      await navigateTo(page, '/dashboard');
      await page.waitForSelector('nav[role="navigation"]', { timeout: 10000 });
      
      // Check navigation landmarks
      const mainNav = page.locator('nav[role="navigation"][aria-label*="Main"]');
      await expect(mainNav).toBeVisible({ timeout: 10000 });
      
      // Open mobile drawer
      const menuButton = page.locator('.md\\:hidden button[aria-expanded]');
      await expect(menuButton).toBeVisible({ timeout: 10000 });
      await menuButton.click();
      await page.waitForTimeout(500);
      
      // Mobile nav should have proper labeling
      const drawer = page.locator('[role="dialog"][aria-modal="true"]');
      await expect(drawer).toBeVisible({ timeout: 5000 });
      
      const mobileNav = drawer.locator('nav[aria-label*="Mobile"]');
      await expect(mobileNav).toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('Mobile Performance', () => {
    test.beforeEach(async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 812 });
      await login(page, TestUsers.developer);
    });

    test('should render mobile navigation quickly', async ({ page }) => {
      const startTime = Date.now();
      
      await navigateTo(page, '/dashboard');
      await page.waitForSelector('nav[role="navigation"]', { timeout: 10000 });
      
      // Menu button should be visible quickly
      const menuButton = page.locator('.md\\:hidden button[aria-expanded]');
      await expect(menuButton).toBeVisible({ timeout: 5000 });
      
      const loadTime = Date.now() - startTime;
      expect(loadTime).toBeLessThan(5000); // Should load in under 5 seconds
    });

    test('should animate drawer smoothly', async ({ page }) => {
      await navigateTo(page, '/dashboard');
      await page.waitForSelector('nav[role="navigation"]', { timeout: 10000 });
      
      // Open drawer and measure animation
      const menuButton = page.locator('.md\\:hidden button[aria-expanded]');
      await expect(menuButton).toBeVisible({ timeout: 10000 });
      
      const startTime = Date.now();
      await menuButton.click();
      
      const drawer = page.locator('[role="dialog"][aria-modal="true"]');
      await expect(drawer).toBeVisible({ timeout: 5000 });
      
      const animationTime = Date.now() - startTime;
      expect(animationTime).toBeLessThan(1500); // Animation should complete quickly
    });
  });
});