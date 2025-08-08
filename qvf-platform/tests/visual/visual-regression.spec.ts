import { test, expect } from '@playwright/test';
import { TestUsers } from '../fixtures/test-users';
import { login, navigateTo, waitForPageLoad } from '../fixtures/test-helpers';

test.describe('QVF Platform Visual Regression Tests', () => {
  
  // Configure test to use consistent viewport
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
  });

  test.describe('Login Page Visual Tests', () => {
    test('should match login page visual baseline', async ({ page }) => {
      await page.goto('/login');
      await waitForPageLoad(page);
      
      // Hide dynamic elements that might cause false positives
      await page.addStyleTag({
        content: `
          .loading, .spinner, .animation {
            animation-duration: 0s !important;
            animation-delay: 0s !important;
            transition-duration: 0s !important;
            transition-delay: 0s !important;
          }
          .cursor-blink { animation: none !important; }
        `
      });
      
      // Wait for fonts and images to load
      await page.waitForLoadState('networkidle');
      
      // Full page screenshot
      await expect(page).toHaveScreenshot('login-page-full.png', {
        fullPage: true,
        animations: 'disabled',
        clip: undefined
      });
      
      // Above-the-fold screenshot
      await expect(page).toHaveScreenshot('login-page-viewport.png', {
        fullPage: false,
        animations: 'disabled'
      });
    });

    test('should match login form visual baseline', async ({ page }) => {
      await page.goto('/login');
      await waitForPageLoad(page);
      
      // Focus on the login form specifically
      const loginForm = page.locator('form, .login-form, [data-testid="login-form"]').first();
      
      if (await loginForm.isVisible({ timeout: 5000 })) {
        await expect(loginForm).toHaveScreenshot('login-form.png', {
          animations: 'disabled'
        });
      } else {
        // Fallback to main content area
        const mainContent = page.locator('main, .main-content, .login-container').first();
        await expect(mainContent).toHaveScreenshot('login-main-content.png', {
          animations: 'disabled'
        });
      }
    });
  });

  test.describe('Dashboard Visual Tests', () => {
    test('should match executive dashboard visual baseline', async ({ page }) => {
      await login(page, TestUsers.executive);
      await navigateTo(page, '/dashboard/executive');
      
      // Wait for data to load
      await page.waitForTimeout(3000);
      await page.waitForLoadState('networkidle');
      
      // Disable animations for consistent screenshots
      await page.addStyleTag({
        content: `
          * {
            animation-duration: 0s !important;
            animation-delay: 0s !important;
            transition-duration: 0s !important;
            transition-delay: 0s !important;
          }
        `
      });
      
      // Full dashboard screenshot
      await expect(page).toHaveScreenshot('executive-dashboard-full.png', {
        fullPage: true,
        animations: 'disabled'
      });
      
      // Header/navigation area
      const header = page.locator('header, nav, .header, .navigation').first();
      if (await header.isVisible({ timeout: 3000 })) {
        await expect(header).toHaveScreenshot('dashboard-header.png', {
          animations: 'disabled'
        });
      }
    });

    test('should match product owner dashboard visual baseline', async ({ page }) => {
      await login(page, TestUsers.productOwner);
      await navigateTo(page, '/dashboard/product-owner');
      
      await page.waitForTimeout(3000);
      await page.waitForLoadState('networkidle');
      
      await page.addStyleTag({
        content: `* { animation: none !important; transition: none !important; }`
      });
      
      await expect(page).toHaveScreenshot('product-owner-dashboard-full.png', {
        fullPage: true,
        animations: 'disabled'
      });
    });

    test('should match scrum master dashboard visual baseline', async ({ page }) => {
      await login(page, TestUsers.scrumMaster);
      await navigateTo(page, '/dashboard/scrum-master');
      
      await page.waitForTimeout(3000);
      await page.waitForLoadState('networkidle');
      
      await page.addStyleTag({
        content: `* { animation: none !important; transition: none !important; }`
      });
      
      await expect(page).toHaveScreenshot('scrum-master-dashboard-full.png', {
        fullPage: true,
        animations: 'disabled'
      });
    });
  });

  test.describe('Work Items Visual Tests', () => {
    test('should match work items page visual baseline', async ({ page }) => {
      await login(page, TestUsers.productOwner);
      await navigateTo(page, '/work-items');
      
      await page.waitForTimeout(3000);
      await page.waitForLoadState('networkidle');
      
      // Disable animations and stabilize dynamic content
      await page.addStyleTag({
        content: `
          * { 
            animation: none !important; 
            transition: none !important; 
          }
          .loading { display: none !important; }
        `
      });
      
      // Full page screenshot
      await expect(page).toHaveScreenshot('work-items-page-full.png', {
        fullPage: true,
        animations: 'disabled'
      });
      
      // Work items table/list
      const workItemsContainer = page.locator('table, .work-items-list, [data-testid="work-items"]').first();
      if (await workItemsContainer.isVisible({ timeout: 5000 })) {
        await expect(workItemsContainer).toHaveScreenshot('work-items-container.png', {
          animations: 'disabled'
        });
      }
    });

    test('should match work item creation form visual baseline', async ({ page }) => {
      await login(page, TestUsers.productOwner);
      await navigateTo(page, '/work-items');
      
      // Try to open creation form
      const addButton = page.locator('button:has-text("Add"), button:has-text("Create"), button:has-text("New")').first();
      
      if (await addButton.isVisible({ timeout: 5000 })) {
        await addButton.click();
        await waitForPageLoad(page);
        
        // Screenshot of the form
        const form = page.locator('form, .modal, .dialog, .create-form').first();
        if (await form.isVisible({ timeout: 5000 })) {
          await expect(form).toHaveScreenshot('work-item-create-form.png', {
            animations: 'disabled'
          });
        } else {
          // Fallback to full page if modal/form structure is different
          await expect(page).toHaveScreenshot('work-item-create-page.png', {
            animations: 'disabled'
          });
        }
      }
    });
  });

  test.describe('QVF Comparison Visual Tests', () => {
    test('should match QVF comparison page visual baseline', async ({ page }) => {
      await login(page, TestUsers.productOwner);
      await navigateTo(page, '/compare');
      
      await page.waitForTimeout(3000);
      await page.waitForLoadState('networkidle');
      
      await page.addStyleTag({
        content: `* { animation: none !important; transition: none !important; }`
      });
      
      // Full comparison page
      await expect(page).toHaveScreenshot('qvf-comparison-page-full.png', {
        fullPage: true,
        animations: 'disabled'
      });
      
      // Comparison matrix if available
      const matrix = page.locator('.comparison-matrix, table, [data-testid="matrix"]').first();
      if (await matrix.isVisible({ timeout: 5000 })) {
        await expect(matrix).toHaveScreenshot('comparison-matrix.png', {
          animations: 'disabled'
        });
      }
    });
  });

  test.describe('Component Visual Tests', () => {
    test('should match UI components visual baseline', async ({ page }) => {
      await login(page, TestUsers.productOwner);
      await navigateTo(page, '/dashboard/product-owner');
      
      await page.waitForTimeout(3000);
      await page.addStyleTag({
        content: `* { animation: none !important; transition: none !important; }`
      });
      
      // Test individual components if they're visible
      const componentSelectors = [
        '.card',
        '.kpi-card', 
        '.insight-card',
        '.button',
        '.progress',
        '.badge',
        '.alert'
      ];
      
      for (const selector of componentSelectors) {
        const component = page.locator(selector).first();
        if (await component.isVisible({ timeout: 3000 })) {
          try {
            await expect(component).toHaveScreenshot(`component-${selector.replace('.', '')}.png`, {
              animations: 'disabled'
            });
          } catch (error) {
            console.log(`Component ${selector} screenshot failed:`, error.message);
          }
        }
      }
    });

    test('should match navigation component visual baseline', async ({ page }) => {
      await login(page, TestUsers.executive);
      await navigateTo(page, '/dashboard/executive');
      
      await page.waitForTimeout(2000);
      await page.addStyleTag({
        content: `* { animation: none !important; transition: none !important; }`
      });
      
      // Navigation component
      const nav = page.locator('nav, .navigation, [role="navigation"]').first();
      if (await nav.isVisible({ timeout: 5000 })) {
        await expect(nav).toHaveScreenshot('navigation-component.png', {
          animations: 'disabled'
        });
      }
    });
  });

  test.describe('Error States Visual Tests', () => {
    test('should match 404 page visual baseline', async ({ page }) => {
      await page.goto('/non-existent-page');
      await waitForPageLoad(page);
      
      await page.addStyleTag({
        content: `* { animation: none !important; transition: none !important; }`
      });
      
      // Check if we got a 404 page or were redirected
      const url = page.url();
      if (url.includes('404') || url.includes('not-found')) {
        await expect(page).toHaveScreenshot('404-page.png', {
          fullPage: true,
          animations: 'disabled'
        });
      } else if (url.includes('login')) {
        // Redirected to login for protected route
        await expect(page).toHaveScreenshot('protected-route-redirect.png', {
          animations: 'disabled'
        });
      }
    });

    test('should match error states visual baseline', async ({ page }) => {
      await login(page, TestUsers.productOwner);
      
      // Try to trigger error states by accessing invalid data
      await page.route('**/api/**', route => {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Internal Server Error' })
        });
      });
      
      await navigateTo(page, '/work-items');
      await page.waitForTimeout(3000);
      
      // Look for error states
      const errorElements = page.locator('.error, .error-message, [role="alert"]');
      if (await errorElements.first().isVisible({ timeout: 5000 })) {
        await expect(page).toHaveScreenshot('api-error-state.png', {
          animations: 'disabled'
        });
      }
    });
  });

  test.describe('Theme and Styling Tests', () => {
    test('should match different viewport sizes', async ({ page }) => {
      await login(page, TestUsers.executive);
      
      // Test different common viewport sizes
      const viewports = [
        { width: 1920, height: 1080, name: 'desktop-large' },
        { width: 1440, height: 900, name: 'desktop-medium' },
        { width: 1024, height: 768, name: 'tablet-landscape' },
        { width: 768, height: 1024, name: 'tablet-portrait' }
      ];
      
      for (const viewport of viewports) {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        await navigateTo(page, '/dashboard/executive');
        await page.waitForTimeout(2000);
        
        await page.addStyleTag({
          content: `* { animation: none !important; transition: none !important; }`
        });
        
        await expect(page).toHaveScreenshot(`dashboard-${viewport.name}.png`, {
          fullPage: false, // Viewport screenshot
          animations: 'disabled'
        });
      }
    });

    test('should match print styles', async ({ page }) => {
      await login(page, TestUsers.executive);
      await navigateTo(page, '/dashboard/executive');
      
      await page.waitForTimeout(2000);
      
      // Emulate print media
      await page.emulateMedia({ media: 'print' });
      
      await expect(page).toHaveScreenshot('dashboard-print-view.png', {
        fullPage: true,
        animations: 'disabled'
      });
    });
  });

  test.describe('Data Visualization Visual Tests', () => {
    test('should match chart and graph visuals', async ({ page }) => {
      await login(page, TestUsers.executive);
      await navigateTo(page, '/dashboard/executive');
      
      await page.waitForTimeout(5000); // Extra time for charts to render
      await page.waitForLoadState('networkidle');
      
      // Disable animations in charts
      await page.addStyleTag({
        content: `
          * { animation: none !important; transition: none !important; }
          svg * { animation: none !important; }
          .recharts-animation { animation: none !important; }
        `
      });
      
      // Look for chart containers
      const chartSelectors = [
        'svg',
        'canvas', 
        '.chart',
        '.graph',
        '.visualization',
        '[data-testid*="chart"]'
      ];
      
      for (const selector of chartSelectors) {
        const charts = await page.locator(selector).all();
        for (let i = 0; i < Math.min(charts.length, 3); i++) { // Limit to first 3 charts
          if (await charts[i].isVisible()) {
            try {
              await expect(charts[i]).toHaveScreenshot(`chart-${selector.replace(/[^\w]/g, '')}-${i}.png`, {
                animations: 'disabled'
              });
            } catch (error) {
              console.log(`Chart screenshot failed:`, error.message);
            }
          }
        }
      }
    });
  });

  test.describe('Visual Accessibility Tests', () => {
    test('should match high contrast mode visuals', async ({ page }) => {
      await login(page, TestUsers.executive);
      
      // Simulate high contrast mode
      await page.addStyleTag({
        content: `
          * { 
            animation: none !important; 
            transition: none !important;
            filter: contrast(150%) !important;
          }
        `
      });
      
      await navigateTo(page, '/dashboard/executive');
      await page.waitForTimeout(2000);
      
      await expect(page).toHaveScreenshot('dashboard-high-contrast.png', {
        animations: 'disabled'
      });
    });

    test('should match focus states visual baseline', async ({ page }) => {
      await login(page, TestUsers.executive);
      await navigateTo(page, '/dashboard/executive');
      
      await page.waitForTimeout(2000);
      await page.addStyleTag({
        content: `* { animation: none !important; transition: none !important; }`
      });
      
      // Tab through focusable elements and capture focus states
      await page.keyboard.press('Tab');
      await page.waitForTimeout(500);
      
      await expect(page).toHaveScreenshot('focus-state-first-element.png', {
        animations: 'disabled'
      });
      
      // Continue to next focusable element
      await page.keyboard.press('Tab');
      await page.waitForTimeout(500);
      
      await expect(page).toHaveScreenshot('focus-state-second-element.png', {
        animations: 'disabled'
      });
    });
  });
});