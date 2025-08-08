import { test, expect, Page } from '@playwright/test';
import path from 'path';

// Test users available
const users = {
  executive: {
    username: 'executive',
    password: 'executive123',
  },
  productOwner: {
    username: 'product_owner',
    password: 'po123',
  },
  scrumMaster: {
    username: 'scrum_master',
    password: 'sm123',
  },
};

// Helper function to wait for page load and ensure elements are visible
async function waitForPageLoad(page: Page, timeout = 5000) {
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1000); // Additional wait for any animations
}

// Helper function to login
async function login(page: Page, username: string, password: string) {
  await page.fill('[data-testid="username"], input[name="username"], input[type="text"]', username);
  await page.fill('[data-testid="password"], input[name="password"], input[type="password"]', password);
  await page.click('[data-testid="login-button"], button[type="submit"], button:has-text("Login"), button:has-text("Sign In")');
  await waitForPageLoad(page);
}

// Helper function to logout
async function logout(page: Page) {
  // Try multiple logout selectors
  const logoutSelectors = [
    '[data-testid="logout-button"]',
    'button:has-text("Logout")',
    'button:has-text("Sign Out")',
    '[aria-label="Logout"]',
    '.logout',
  ];
  
  let loggedOut = false;
  for (const selector of logoutSelectors) {
    try {
      if (await page.isVisible(selector, { timeout: 1000 })) {
        await page.click(selector);
        await waitForPageLoad(page);
        loggedOut = true;
        break;
      }
    } catch (error) {
      // Continue to next selector
    }
  }
  
  if (!loggedOut) {
    // Try navigating to login page directly
    await page.goto('/login');
    await waitForPageLoad(page);
  }
}

test.describe('QVF Platform Screenshot Capture', () => {
  test.beforeEach(async ({ page }) => {
    // Set viewport size for consistent screenshots
    await page.setViewportSize({ width: 1440, height: 900 });
  });

  test('Capture QVF Platform Screenshots', async ({ page }) => {
    // 1. Navigate to QVF Platform and take login page screenshot
    console.log('Step 1: Navigating to QVF Platform...');
    await page.goto('/');
    await waitForPageLoad(page);
    
    // Take login page screenshot
    await page.screenshot({
      path: 'qvf-01-login-page.png',
      fullPage: true,
    });
    console.log('✅ Login page screenshot captured');

    // 2. Login as Executive user
    console.log('Step 2: Logging in as Executive user...');
    await login(page, users.executive.username, users.executive.password);
    
    // Wait for dashboard to load and take screenshot
    await waitForPageLoad(page);
    await page.screenshot({
      path: 'qvf-02-executive-dashboard.png',
      fullPage: true,
    });
    console.log('✅ Executive dashboard screenshot captured');

    // Take additional screenshots of different sections if available
    try {
      // Try to capture metrics or overview section
      const metricsSection = await page.$('.metrics, .overview, [data-testid="metrics"]');
      if (metricsSection) {
        await page.screenshot({
          path: 'qvf-03-executive-metrics.png',
          fullPage: true,
        });
        console.log('✅ Executive metrics screenshot captured');
      }
    } catch (error) {
      console.log('ℹ️  Additional executive screenshots not available');
    }

    // 3. Logout and login as Product Owner
    console.log('Step 3: Switching to Product Owner user...');
    await logout(page);
    await login(page, users.productOwner.username, users.productOwner.password);
    
    await waitForPageLoad(page);
    await page.screenshot({
      path: 'qvf-04-product-owner-dashboard.png',
      fullPage: true,
    });
    console.log('✅ Product Owner dashboard screenshot captured');

    // 4. Navigate to Work Items page
    console.log('Step 4: Navigating to Work Items page...');
    const workItemsSelectors = [
      'a:has-text("Work Items")',
      'a[href*="work-items"]',
      'a[href*="workitems"]',
      '[data-testid="work-items"]',
      'nav a:has-text("Items")',
    ];
    
    let workItemsFound = false;
    for (const selector of workItemsSelectors) {
      try {
        if (await page.isVisible(selector, { timeout: 2000 })) {
          await page.click(selector);
          await waitForPageLoad(page);
          workItemsFound = true;
          break;
        }
      } catch (error) {
        // Continue to next selector
      }
    }
    
    if (!workItemsFound) {
      // Try direct navigation
      try {
        await page.goto('/work-items');
        await waitForPageLoad(page);
        workItemsFound = true;
      } catch (error) {
        try {
          await page.goto('/workitems');
          await waitForPageLoad(page);
          workItemsFound = true;
        } catch (error) {
          console.log('⚠️  Work Items page not found, continuing...');
        }
      }
    }
    
    if (workItemsFound) {
      await page.screenshot({
        path: 'qvf-05-work-items-page.png',
        fullPage: true,
      });
      console.log('✅ Work Items page screenshot captured');
    }

    // 5. Navigate to QVF Comparison page
    console.log('Step 5: Navigating to QVF Comparison page...');
    const qvfComparisonSelectors = [
      'a:has-text("QVF Comparison")',
      'a:has-text("Comparison")',
      'a[href*="comparison"]',
      'a[href*="qvf"]',
      '[data-testid="qvf-comparison"]',
      'nav a:has-text("QVF")',
    ];
    
    let comparisonFound = false;
    for (const selector of qvfComparisonSelectors) {
      try {
        if (await page.isVisible(selector, { timeout: 2000 })) {
          await page.click(selector);
          await waitForPageLoad(page);
          comparisonFound = true;
          break;
        }
      } catch (error) {
        // Continue to next selector
      }
    }
    
    if (!comparisonFound) {
      // Try direct navigation
      try {
        await page.goto('/qvf-comparison');
        await waitForPageLoad(page);
        comparisonFound = true;
      } catch (error) {
        try {
          await page.goto('/comparison');
          await waitForPageLoad(page);
          comparisonFound = true;
        } catch (error) {
          console.log('⚠️  QVF Comparison page not found, continuing...');
        }
      }
    }
    
    if (comparisonFound) {
      await page.screenshot({
        path: 'qvf-06-qvf-comparison-page.png',
        fullPage: true,
      });
      console.log('✅ QVF Comparison page screenshot captured');
    }

    // 6. Take a final screenshot of the current state
    await page.screenshot({
      path: 'qvf-07-final-state.png',
      fullPage: true,
    });
    console.log('✅ Final state screenshot captured');

    console.log('🎉 All screenshots captured successfully!');
    console.log('Screenshots saved in the qvf-platform directory:');
    console.log('  - qvf-01-login-page.png');
    console.log('  - qvf-02-executive-dashboard.png');
    console.log('  - qvf-03-executive-metrics.png (if available)');
    console.log('  - qvf-04-product-owner-dashboard.png');
    console.log('  - qvf-05-work-items-page.png (if available)');
    console.log('  - qvf-06-qvf-comparison-page.png (if available)');
    console.log('  - qvf-07-final-state.png');
  });

  test('Capture Mobile Screenshots', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 812 });
    
    console.log('Capturing mobile screenshots...');
    
    await page.goto('/');
    await waitForPageLoad(page);
    
    await page.screenshot({
      path: 'qvf-mobile-01-login.png',
      fullPage: true,
    });

    // Login as executive
    await login(page, users.executive.username, users.executive.password);
    await waitForPageLoad(page);
    
    await page.screenshot({
      path: 'qvf-mobile-02-executive-dashboard.png',
      fullPage: true,
    });

    console.log('✅ Mobile screenshots captured');
  });
});