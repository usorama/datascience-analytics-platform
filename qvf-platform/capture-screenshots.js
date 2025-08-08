#!/usr/bin/env node

/**
 * QVF Platform Screenshot Capture Script
 * 
 * This script uses Playwright to capture screenshots of the QVF Platform.
 * Make sure the application is running at http://localhost:3006 before running this script.
 */

const { chromium } = require('playwright');
const path = require('path');

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

// Helper function to wait for page load
async function waitForPageLoad(page, timeout = 5000) {
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1000); // Additional wait for animations
}

// Helper function to login
async function login(page, username, password) {
  console.log(`  Logging in as ${username}...`);
  
  // Try multiple input selectors for username
  const usernameSelectors = [
    '[data-testid="username"]',
    'input[name="username"]',
    'input[type="text"]',
    'input[placeholder*="username" i]',
    'input[placeholder*="email" i]',
  ];
  
  let usernameInput = null;
  for (const selector of usernameSelectors) {
    try {
      if (await page.isVisible(selector, { timeout: 1000 })) {
        usernameInput = await page.$(selector);
        break;
      }
    } catch (error) {
      // Continue to next selector
    }
  }
  
  if (usernameInput) {
    await page.fill(usernameSelectors.find(async (s) => await page.isVisible(s, { timeout: 1000 })), username);
  } else {
    console.log('  ⚠️  Username input not found, trying to type directly');
    await page.keyboard.type(username);
    await page.keyboard.press('Tab');
  }
  
  // Try multiple input selectors for password
  const passwordSelectors = [
    '[data-testid="password"]',
    'input[name="password"]',
    'input[type="password"]',
    'input[placeholder*="password" i]',
  ];
  
  let passwordInput = null;
  for (const selector of passwordSelectors) {
    try {
      if (await page.isVisible(selector, { timeout: 1000 })) {
        passwordInput = await page.$(selector);
        break;
      }
    } catch (error) {
      // Continue to next selector
    }
  }
  
  if (passwordInput) {
    await page.fill(passwordSelectors.find(async (s) => await page.isVisible(s, { timeout: 1000 })), password);
  } else {
    console.log('  ⚠️  Password input not found, trying to type directly');
    await page.keyboard.type(password);
  }
  
  // Try multiple button selectors for login
  const loginButtonSelectors = [
    '[data-testid="login-button"]',
    'button[type="submit"]',
    'button:has-text("Login")',
    'button:has-text("Sign In")',
    'input[type="submit"]',
  ];
  
  let loginButton = null;
  for (const selector of loginButtonSelectors) {
    try {
      if (await page.isVisible(selector, { timeout: 1000 })) {
        await page.click(selector);
        loginButton = true;
        break;
      }
    } catch (error) {
      // Continue to next selector
    }
  }
  
  if (!loginButton) {
    console.log('  ⚠️  Login button not found, trying Enter key');
    await page.keyboard.press('Enter');
  }
  
  await waitForPageLoad(page);
  console.log('  ✅ Login completed');
}

// Helper function to logout
async function logout(page) {
  console.log('  Logging out...');
  
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
    console.log('  ⚠️  Logout button not found, navigating to login page');
    await page.goto('http://localhost:3006/login');
    await waitForPageLoad(page);
  }
  
  console.log('  ✅ Logout completed');
}

async function captureScreenshots() {
  console.log('🚀 Starting QVF Platform Screenshot Capture...\n');
  
  // Launch browser
  const browser = await chromium.launch({ headless: false }); // Set to true for headless mode
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
  });
  const page = await context.newPage();
  
  try {
    // 1. Navigate to QVF Platform and capture login page
    console.log('📸 Step 1: Capturing login page...');
    await page.goto('http://localhost:3006');
    await waitForPageLoad(page);
    
    await page.screenshot({
      path: path.join(__dirname, 'qvf-01-login-page.png'),
      fullPage: true,
    });
    console.log('  ✅ Login page screenshot saved\n');
    
    // 2. Login as Executive user
    console.log('📸 Step 2: Logging in as Executive and capturing dashboard...');
    await login(page, users.executive.username, users.executive.password);
    
    await page.screenshot({
      path: path.join(__dirname, 'qvf-02-executive-dashboard.png'),
      fullPage: true,
    });
    console.log('  ✅ Executive dashboard screenshot saved\n');
    
    // 3. Try to capture additional executive views
    console.log('📸 Step 3: Capturing additional executive views...');
    try {
      // Check for navigation menu or tabs
      const navItems = await page.$$('nav a, .nav-link, [role="tab"]');
      if (navItems.length > 0) {
        await page.screenshot({
          path: path.join(__dirname, 'qvf-03-executive-full-view.png'),
          fullPage: true,
        });
        console.log('  ✅ Additional executive view captured');
      }
    } catch (error) {
      console.log('  ℹ️  Additional executive views not available');
    }
    console.log('');
    
    // 4. Logout and login as Product Owner
    console.log('📸 Step 4: Switching to Product Owner...');
    await logout(page);
    await login(page, users.productOwner.username, users.productOwner.password);
    
    await page.screenshot({
      path: path.join(__dirname, 'qvf-04-product-owner-dashboard.png'),
      fullPage: true,
    });
    console.log('  ✅ Product Owner dashboard screenshot saved\n');
    
    // 5. Navigate to Work Items page
    console.log('📸 Step 5: Searching for Work Items page...');
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
      const workItemsUrls = ['/work-items', '/workitems', '/items'];
      for (const url of workItemsUrls) {
        try {
          await page.goto(`http://localhost:3006${url}`);
          await waitForPageLoad(page);
          // Check if we're not on a 404 page
          const pageText = await page.textContent('body');
          if (!pageText.toLowerCase().includes('404') && !pageText.toLowerCase().includes('not found')) {
            workItemsFound = true;
            break;
          }
        } catch (error) {
          // Continue to next URL
        }
      }
    }
    
    if (workItemsFound) {
      await page.screenshot({
        path: path.join(__dirname, 'qvf-05-work-items-page.png'),
        fullPage: true,
      });
      console.log('  ✅ Work Items page screenshot saved');
    } else {
      console.log('  ⚠️  Work Items page not found');
    }
    console.log('');
    
    // 6. Navigate to QVF Comparison page
    console.log('📸 Step 6: Searching for QVF Comparison page...');
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
      const comparisonUrls = ['/qvf-comparison', '/comparison', '/qvf'];
      for (const url of comparisonUrls) {
        try {
          await page.goto(`http://localhost:3006${url}`);
          await waitForPageLoad(page);
          // Check if we're not on a 404 page
          const pageText = await page.textContent('body');
          if (!pageText.toLowerCase().includes('404') && !pageText.toLowerCase().includes('not found')) {
            comparisonFound = true;
            break;
          }
        } catch (error) {
          // Continue to next URL
        }
      }
    }
    
    if (comparisonFound) {
      await page.screenshot({
        path: path.join(__dirname, 'qvf-06-qvf-comparison-page.png'),
        fullPage: true,
      });
      console.log('  ✅ QVF Comparison page screenshot saved');
    } else {
      console.log('  ⚠️  QVF Comparison page not found');
    }
    console.log('');
    
    // 7. Capture mobile view
    console.log('📸 Step 7: Capturing mobile view...');
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto('http://localhost:3006');
    await waitForPageLoad(page);
    
    await page.screenshot({
      path: path.join(__dirname, 'qvf-07-mobile-login.png'),
      fullPage: true,
    });
    
    // Login on mobile and capture dashboard
    await login(page, users.executive.username, users.executive.password);
    await page.screenshot({
      path: path.join(__dirname, 'qvf-08-mobile-dashboard.png'),
      fullPage: true,
    });
    console.log('  ✅ Mobile screenshots saved\n');
    
    // 8. Final screenshot
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.screenshot({
      path: path.join(__dirname, 'qvf-09-final-state.png'),
      fullPage: true,
    });
    
    console.log('🎉 All screenshots captured successfully!');
    console.log('\nScreenshots saved:');
    console.log('  • qvf-01-login-page.png - Login page');
    console.log('  • qvf-02-executive-dashboard.png - Executive dashboard');
    console.log('  • qvf-03-executive-full-view.png - Additional executive view (if available)');
    console.log('  • qvf-04-product-owner-dashboard.png - Product Owner dashboard');
    console.log('  • qvf-05-work-items-page.png - Work Items page (if available)');
    console.log('  • qvf-06-qvf-comparison-page.png - QVF Comparison page (if available)');
    console.log('  • qvf-07-mobile-login.png - Mobile login view');
    console.log('  • qvf-08-mobile-dashboard.png - Mobile dashboard view');
    console.log('  • qvf-09-final-state.png - Final state');
    
  } catch (error) {
    console.error('❌ Error during screenshot capture:', error);
  } finally {
    await browser.close();
  }
}

// Check if application is running
async function checkApplicationStatus() {
  console.log('🔍 Checking if QVF Platform is running at http://localhost:3006...');
  
  try {
    const fetch = (await import('node-fetch')).default;
    const response = await fetch('http://localhost:3006', { 
      timeout: 5000,
      signal: AbortSignal.timeout(5000)
    });
    
    if (response.ok) {
      console.log('✅ QVF Platform is running and accessible\n');
      return true;
    } else {
      console.log(`⚠️  QVF Platform responded with status: ${response.status}\n`);
      return false;
    }
  } catch (error) {
    console.log('❌ QVF Platform is not accessible at http://localhost:3006');
    console.log('   Please make sure the application is running with: pnpm run dev\n');
    return false;
  }
}

// Main execution
async function main() {
  const isRunning = await checkApplicationStatus();
  
  if (isRunning) {
    await captureScreenshots();
  } else {
    console.log('💡 To start the QVF Platform, run:');
    console.log('   cd qvf-platform');
    console.log('   pnpm install');
    console.log('   pnpm run dev');
    console.log('   Then run this script again.');
  }
}

main().catch(console.error);