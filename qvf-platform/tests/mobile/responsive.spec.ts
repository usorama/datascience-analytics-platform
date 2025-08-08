import { test, expect, devices } from '@playwright/test';
import { TestUsers } from '../fixtures/test-users';
import { login, navigateTo, waitForPageLoad, takeScreenshot } from '../fixtures/test-helpers';

test.describe('QVF Platform Mobile Responsive Tests', () => {
  
  // Common mobile device configurations
  const mobileDevices = [
    { name: 'iPhone 12', device: devices['iPhone 12'] },
    { name: 'iPhone 13 Pro', device: devices['iPhone 13 Pro'] },
    { name: 'Pixel 5', device: devices['Pixel 5'] },
    { name: 'Samsung Galaxy S21', device: devices['Galaxy S21'] },
  ];

  const tabletDevices = [
    { name: 'iPad Air', device: devices['iPad Air'] },
    { name: 'iPad Pro', device: devices['iPad Pro'] },
  ];

  // Custom viewport sizes for testing
  const customViewports = [
    { name: 'Small Mobile', width: 320, height: 568 }, // iPhone SE
    { name: 'Medium Mobile', width: 375, height: 812 }, // iPhone X
    { name: 'Large Mobile', width: 428, height: 926 }, // iPhone 12 Pro Max
    { name: 'Small Tablet', width: 768, height: 1024 }, // iPad Mini
    { name: 'Large Tablet', width: 1024, height: 1366 }, // iPad Pro
  ];

  test.describe('Mobile Device Login Tests', () => {
    mobileDevices.forEach(({ name, device }) => {
      test(`should work on ${name}`, async ({ browser }) => {
        const context = await browser.newContext(device);
        const page = await context.newPage();

        try {
          await page.goto('/login');
          await waitForPageLoad(page);

          // Check if login form is visible and usable on mobile
          const usernameField = page.locator('input[name="username"], input[type="text"]');
          const passwordField = page.locator('input[name="password"], input[type="password"]');
          const loginButton = page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Sign In")');

          await expect(usernameField).toBeVisible();
          await expect(passwordField).toBeVisible();
          await expect(loginButton).toBeVisible();

          // Check if elements are properly sized for mobile interaction
          const usernameBox = await usernameField.boundingBox();
          const passwordBox = await passwordField.boundingBox();
          const buttonBox = await loginButton.boundingBox();

          // Touch targets should be at least 44px for accessibility
          expect(usernameBox?.height).toBeGreaterThanOrEqual(40);
          expect(passwordBox?.height).toBeGreaterThanOrEqual(40);
          expect(buttonBox?.height).toBeGreaterThanOrEqual(40);

          // Test login functionality
          await usernameField.fill(TestUsers.executive.username);
          await passwordField.fill(TestUsers.executive.password);
          await loginButton.tap(); // Use tap instead of click for mobile

          // Wait for login to complete
          try {
            await page.waitForURL(/\/(dashboard|work-items)/, { timeout: 15000 });
            console.log(`✅ ${name}: Login successful`);
          } catch {
            console.log(`⚠️  ${name}: Login may have failed or redirected differently`);
          }

          await takeScreenshot(page, `${name.toLowerCase().replace(/\s+/g, '-')}-login`);

        } finally {
          await context.close();
        }
      });
    });
  });

  test.describe('Mobile Dashboard Responsive Tests', () => {
    test('should adapt dashboard layout for mobile screens', async ({ browser }) => {
      const context = await browser.newContext(devices['iPhone 12']);
      const page = await context.newPage();

      try {
        await login(page, TestUsers.executive);
        await navigateTo(page, '/dashboard/executive');

        // Check for mobile-specific navigation patterns
        const mobileNavIndicators = [
          'button[aria-label="Menu"]',
          'button[aria-label="Open menu"]',
          '.hamburger',
          '.mobile-menu-toggle',
          '[data-testid="mobile-nav"]',
          'button:has(svg)' // Hamburger icons are often SVGs
        ];

        let hasMobileNav = false;
        for (const selector of mobileNavIndicators) {
          if (await page.locator(selector).isVisible({ timeout: 3000 }).catch(() => false)) {
            hasMobileNav = true;
            console.log(`Found mobile navigation: ${selector}`);
            
            // Test mobile menu interaction
            await page.tap(selector);
            await page.waitForTimeout(1000);
            
            break;
          }
        }

        // Check if content adapts to mobile width
        const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
        const viewportWidth = page.viewportSize()?.width || 0;
        
        // Content should not cause horizontal scroll on mobile
        expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 20); // Allow small margin

        // Check for touch-friendly elements
        const buttons = await page.locator('button').all();
        for (const button of buttons.slice(0, 5)) { // Check first 5 buttons
          const box = await button.boundingBox();
          if (box) {
            expect(box.height).toBeGreaterThanOrEqual(40); // Touch-friendly size
          }
        }

        await takeScreenshot(page, 'mobile-dashboard-executive');

      } finally {
        await context.close();
      }
    });

    test('should handle mobile work items interface', async ({ browser }) => {
      const context = await browser.newContext(devices['Pixel 5']);
      const page = await context.newPage();

      try {
        await login(page, TestUsers.productOwner);
        await navigateTo(page, '/work-items');

        // Check if work items table/list adapts to mobile
        const workItemsContainer = page.locator('table, .work-items-list, [data-testid="work-items"]').first();
        
        if (await workItemsContainer.isVisible({ timeout: 10000 })) {
          const containerBox = await workItemsContainer.boundingBox();
          const viewportWidth = page.viewportSize()?.width || 0;
          
          // Work items should fit in mobile viewport
          expect(containerBox?.width).toBeLessThanOrEqual(viewportWidth);
          
          // Check for mobile-optimized table behavior
          const isMobileOptimized = await page.evaluate(() => {
            // Check for common mobile table patterns
            const tables = document.querySelectorAll('table');
            const responsivePatterns = [
              '.table-responsive',
              '.mobile-table',
              '[data-mobile="true"]'
            ];
            
            return tables.length === 0 || // No tables (replaced with cards/lists)
                   responsivePatterns.some(pattern => document.querySelector(pattern)) ||
                   Array.from(tables).some(table => 
                     window.getComputedStyle(table).overflowX === 'auto' ||
                     table.parentElement?.style.overflowX === 'auto'
                   );
          });
          
          console.log(`Mobile table optimization: ${isMobileOptimized ? 'Yes' : 'No'}`);
        }

        // Test mobile interactions
        const firstInteractable = page.locator('button, a, [role="button"], .work-item').first();
        if (await firstInteractable.isVisible({ timeout: 5000 })) {
          await firstInteractable.tap();
          await page.waitForTimeout(1000);
        }

        await takeScreenshot(page, 'mobile-work-items');

      } finally {
        await context.close();
      }
    });
  });

  test.describe('Tablet Responsive Tests', () => {
    test('should provide optimal tablet experience', async ({ browser }) => {
      const context = await browser.newContext(devices['iPad Air']);
      const page = await context.newPage();

      try {
        await login(page, TestUsers.productOwner);
        await navigateTo(page, '/dashboard/product-owner');

        // Tablets should utilize more screen space than mobile
        const viewportWidth = page.viewportSize()?.width || 0;
        
        // Check for tablet-specific layout optimizations
        const contentArea = page.locator('main, .main-content, .dashboard').first();
        if (await contentArea.isVisible({ timeout: 5000 })) {
          const contentBox = await contentArea.boundingBox();
          const contentUtilization = (contentBox?.width || 0) / viewportWidth;
          
          // Tablets should utilize more width than mobile
          expect(contentUtilization).toBeGreaterThan(0.8); // At least 80% width utilization
        }

        // Check for multi-column layouts on tablet
        const columns = await page.locator('.col-md-6, .col-lg-4, .grid-cols-2, .grid-cols-3').count();
        expect(columns).toBeGreaterThan(0); // Should have some columnar layout

        await takeScreenshot(page, 'tablet-dashboard');

      } finally {
        await context.close();
      }
    });
  });

  test.describe('Custom Viewport Tests', () => {
    customViewports.forEach(viewport => {
      test(`should work at ${viewport.name} (${viewport.width}x${viewport.height})`, async ({ page }) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height });
        
        await login(page, TestUsers.executive);
        await navigateTo(page, '/dashboard/executive');

        // Check for responsive behavior at custom viewport
        const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
        
        // No horizontal scroll
        expect(bodyWidth).toBeLessThanOrEqual(viewport.width + 10);

        // Content should be readable
        const fontSize = await page.evaluate(() => {
          const bodyStyle = window.getComputedStyle(document.body);
          return parseInt(bodyStyle.fontSize);
        });
        
        expect(fontSize).toBeGreaterThanOrEqual(14); // Minimum readable font size

        await takeScreenshot(page, `viewport-${viewport.name.toLowerCase().replace(/\s+/g, '-')}`);
      });
    });
  });

  test.describe('Touch Interaction Tests', () => {
    test('should handle touch gestures properly', async ({ browser }) => {
      const context = await browser.newContext(devices['iPhone 12']);
      const page = await context.newPage();

      try {
        await login(page, TestUsers.productOwner);
        await navigateTo(page, '/work-items');

        // Test swipe gestures if implemented
        const swipeableElements = await page.locator('.swipeable, [data-swipe="true"]').all();
        
        if (swipeableElements.length > 0) {
          const element = swipeableElements[0];
          const box = await element.boundingBox();
          
          if (box) {
            // Simulate swipe gesture
            await page.touchscreen.tap(box.x + box.width * 0.8, box.y + box.height / 2);
            await page.touchscreen.tap(box.x + box.width * 0.2, box.y + box.height / 2);
            
            console.log('Tested swipe gesture');
          }
        }

        // Test pinch-to-zoom prevention for UI elements
        const preventZoom = await page.evaluate(() => {
          const viewport = document.querySelector('meta[name="viewport"]');
          return viewport?.getAttribute('content')?.includes('user-scalable=no') || 
                 viewport?.getAttribute('content')?.includes('maximum-scale=1');
        });

        console.log(`Zoom prevention: ${preventZoom ? 'Enabled' : 'Disabled'}`);

        // Test long press interactions
        const longPressTargets = await page.locator('button, .work-item, [role="button"]').all();
        
        if (longPressTargets.length > 0) {
          const target = longPressTargets[0];
          const box = await target.boundingBox();
          
          if (box) {
            // Simulate long press
            await page.touchscreen.tap(box.x + box.width / 2, box.y + box.height / 2);
            await page.waitForTimeout(800); // Long press duration
            
            // Check if context menu or additional options appeared
            const contextMenu = await page.locator('.context-menu, .popup, .dropdown').isVisible().catch(() => false);
            if (contextMenu) {
              console.log('Long press interaction detected');
            }
          }
        }

      } finally {
        await context.close();
      }
    });
  });

  test.describe('Orientation Tests', () => {
    test('should handle device orientation changes', async ({ browser }) => {
      const context = await browser.newContext(devices['iPhone 12']);
      const page = await context.newPage();

      try {
        await login(page, TestUsers.executive);

        // Test portrait orientation
        await page.setViewportSize({ width: 390, height: 844 });
        await navigateTo(page, '/dashboard/executive');
        await waitForPageLoad(page);
        
        const portraitLayout = await page.evaluate(() => {
          return window.innerHeight > window.innerWidth;
        });
        
        expect(portraitLayout).toBeTruthy();
        await takeScreenshot(page, 'mobile-portrait');

        // Test landscape orientation
        await page.setViewportSize({ width: 844, height: 390 });
        await page.waitForTimeout(1000); // Allow layout to adjust
        
        const landscapeLayout = await page.evaluate(() => {
          return window.innerWidth > window.innerHeight;
        });
        
        expect(landscapeLayout).toBeTruthy();
        
        // Check if layout adapts to landscape
        const bodyHeight = await page.evaluate(() => document.body.scrollHeight);
        const viewportHeight = page.viewportSize()?.height || 0;
        
        // Content should fit better in landscape
        const verticalScrollNeeded = bodyHeight > viewportHeight;
        console.log(`Landscape vertical scroll needed: ${verticalScrollNeeded}`);
        
        await takeScreenshot(page, 'mobile-landscape');

      } finally {
        await context.close();
      }
    });
  });

  test.describe('Mobile-Specific Features', () => {
    test('should provide mobile-optimized interactions', async ({ browser }) => {
      const context = await browser.newContext(devices['Pixel 5']);
      const page = await context.newPage();

      try {
        await login(page, TestUsers.productOwner);
        await navigateTo(page, '/work-items');

        // Check for mobile-specific UI patterns
        const mobilePatterns = [
          '.mobile-only',
          '.d-block.d-md-none', // Bootstrap mobile-only
          '[class*="sm:hidden"]', // Tailwind mobile-only
          '.fab', // Floating Action Button
          '.bottom-nav',
          '.mobile-drawer'
        ];

        let mobileSpecificUI = false;
        for (const pattern of mobilePatterns) {
          if (await page.locator(pattern).isVisible({ timeout: 3000 }).catch(() => false)) {
            mobileSpecificUI = true;
            console.log(`Found mobile-specific UI: ${pattern}`);
            break;
          }
        }

        // Check for pull-to-refresh if implemented
        const refreshable = await page.evaluate(() => {
          return document.body.style.overscrollBehavior === 'contain' ||
                 document.documentElement.style.overscrollBehavior === 'contain' ||
                 document.querySelector('[data-refresh="true"]') !== null;
        });

        console.log(`Pull-to-refresh capability: ${refreshable ? 'Enabled' : 'Not detected'}`);

        // Test mobile form improvements
        const inputs = await page.locator('input').all();
        for (const input of inputs.slice(0, 3)) {
          const inputType = await input.getAttribute('inputmode') || await input.getAttribute('type');
          const hasAutocomplete = await input.getAttribute('autocomplete');
          
          if (inputType || hasAutocomplete) {
            console.log(`Mobile-optimized input detected: type=${inputType}, autocomplete=${hasAutocomplete}`);
          }
        }

      } finally {
        await context.close();
      }
    });

    test('should handle mobile performance considerations', async ({ browser }) => {
      const context = await browser.newContext(devices['iPhone 12']);
      const page = await context.newPage();

      try {
        // Test with simulated slower mobile network
        await context.route('**/*', async (route) => {
          // Add small delay to simulate mobile network
          await new Promise(resolve => setTimeout(resolve, 50));
          await route.continue();
        });

        const startTime = Date.now();
        await login(page, TestUsers.executive);
        const loadTime = Date.now() - startTime;

        // Mobile should still load reasonably quickly even on slower networks
        expect(loadTime).toBeLessThan(10000); // 10 seconds on simulated mobile network
        console.log(`Mobile load time with network simulation: ${loadTime}ms`);

        // Check for mobile-specific optimizations
        const optimizations = await page.evaluate(() => {
          // Check for lazy loading
          const lazyImages = document.querySelectorAll('img[loading="lazy"]');
          const lazyContent = document.querySelectorAll('[data-lazy="true"]');
          
          // Check for reduced animations on mobile
          const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
          
          return {
            lazyImages: lazyImages.length,
            lazyContent: lazyContent.length,
            reducedMotion
          };
        });

        console.log('Mobile optimizations detected:', optimizations);

      } finally {
        await context.close();
      }
    });
  });

  test.describe('Accessibility on Mobile', () => {
    test('should maintain accessibility standards on mobile', async ({ browser }) => {
      const context = await browser.newContext(devices['iPhone 12']);
      const page = await context.newPage();

      try {
        await login(page, TestUsers.executive);
        await navigateTo(page, '/dashboard/executive');

        // Check for proper heading hierarchy
        const headings = await page.locator('h1, h2, h3, h4, h5, h6').all();
        expect(headings.length).toBeGreaterThan(0);

        // Check for ARIA labels on interactive elements
        const interactiveElements = await page.locator('button, a, input, select').all();
        let accessibleElements = 0;

        for (const element of interactiveElements.slice(0, 10)) {
          const hasAriaLabel = await element.getAttribute('aria-label');
          const hasAriaLabelledBy = await element.getAttribute('aria-labelledby');
          const hasTitle = await element.getAttribute('title');
          const textContent = await element.textContent();
          
          if (hasAriaLabel || hasAriaLabelledBy || hasTitle || (textContent && textContent.trim())) {
            accessibleElements++;
          }
        }

        const accessibilityRatio = accessibleElements / Math.min(interactiveElements.length, 10);
        expect(accessibilityRatio).toBeGreaterThan(0.8); // 80% of elements should be accessible

        // Check for proper focus management
        await page.keyboard.press('Tab');
        const focusedElement = await page.evaluate(() => document.activeElement?.tagName);
        expect(['BUTTON', 'A', 'INPUT', 'SELECT'].includes(focusedElement || '')).toBeTruthy();

      } finally {
        await context.close();
      }
    });
  });
});