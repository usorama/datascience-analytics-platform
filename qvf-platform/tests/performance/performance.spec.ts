import { test, expect } from '@playwright/test';
import { TestUsers } from '../fixtures/test-users';
import { login, navigateTo, waitForPageLoad } from '../fixtures/test-helpers';

test.describe('QVF Platform Performance Tests', () => {
  
  test.describe('Page Load Performance', () => {
    test('should load login page within performance budget', async ({ page }) => {
      const startTime = Date.now();
      
      // Monitor network requests
      const requests: { url: string; responseTime: number; size: number }[] = [];
      
      page.on('response', async (response) => {
        const request = response.request();
        const responseTime = Date.now() - startTime;
        let size = 0;
        
        try {
          const headers = response.headers();
          size = parseInt(headers['content-length'] || '0');
        } catch {
          // Size calculation might fail
        }
        
        requests.push({
          url: request.url(),
          responseTime,
          size
        });
      });
      
      // Navigate to login page
      await page.goto('/login');
      await waitForPageLoad(page);
      
      const loadTime = Date.now() - startTime;
      
      // Performance assertions
      expect(loadTime).toBeLessThan(3000); // Should load within 3 seconds
      
      // Log performance metrics
      console.log(`Login page loaded in ${loadTime}ms`);
      console.log(`Total requests: ${requests.length}`);
      
      const slowRequests = requests.filter(req => req.responseTime > 1000);
      if (slowRequests.length > 0) {
        console.log('Slow requests (>1s):', slowRequests.map(req => ({
          url: req.url,
          time: `${req.responseTime}ms`
        })));
      }
    });

    test('should load dashboard pages within performance budget', async ({ page }) => {
      const performanceMetrics: Array<{ page: string; loadTime: number; requests: number }> = [];
      
      await login(page, TestUsers.executive);
      
      const dashboardRoutes = [
        '/dashboard/executive',
        '/dashboard/product-owner', 
        '/dashboard/scrum-master'
      ];
      
      for (const route of dashboardRoutes) {
        const startTime = Date.now();
        let requestCount = 0;
        
        const requestListener = () => requestCount++;
        page.on('request', requestListener);
        
        try {
          await navigateTo(page, route);
          await waitForPageLoad(page);
          
          const loadTime = Date.now() - startTime;
          
          performanceMetrics.push({
            page: route,
            loadTime,
            requests: requestCount
          });
          
          // Performance budget: 5 seconds for dashboard pages
          expect(loadTime).toBeLessThan(5000);
          
          console.log(`${route} loaded in ${loadTime}ms with ${requestCount} requests`);
          
        } catch (error) {
          console.log(`${route} failed to load or access denied`);
        } finally {
          page.off('request', requestListener);
        }
        
        // Brief pause between routes
        await page.waitForTimeout(1000);
      }
      
      // Calculate average performance
      const avgLoadTime = performanceMetrics.reduce((sum, metric) => sum + metric.loadTime, 0) / performanceMetrics.length;
      console.log(`Average dashboard load time: ${Math.round(avgLoadTime)}ms`);
    });

    test('should load work items page efficiently', async ({ page }) => {
      await login(page, TestUsers.productOwner);
      
      const startTime = Date.now();
      let apiCalls = 0;
      
      // Monitor API calls
      page.on('response', (response) => {
        if (response.url().includes('/api/')) {
          apiCalls++;
        }
      });
      
      await navigateTo(page, '/work-items');
      await waitForPageLoad(page);
      
      const loadTime = Date.now() - startTime;
      
      // Performance assertions
      expect(loadTime).toBeLessThan(4000); // 4 second budget for work items
      expect(apiCalls).toBeLessThan(10); // Should not make excessive API calls
      
      console.log(`Work items page: ${loadTime}ms, API calls: ${apiCalls}`);
    });
  });

  test.describe('API Performance', () => {
    test('should have fast authentication API response', async ({ page }) => {
      await page.goto('/login');
      
      // Monitor authentication API call
      let authResponseTime = 0;
      
      page.on('response', async (response) => {
        if (response.url().includes('/auth/token') || response.url().includes('/login')) {
          authResponseTime = response.timing()?.responseTime || 0;
        }
      });
      
      const startTime = Date.now();
      
      // Perform login
      await page.fill('input[name="username"], input[type="text"]', TestUsers.executive.username);
      await page.fill('input[name="password"], input[type="password"]', TestUsers.executive.password);
      await page.click('button[type="submit"], button:has-text("Login")');
      
      // Wait for login completion
      await page.waitForURL(/\/(dashboard|work-items)/, { timeout: 10000 });
      
      const totalAuthTime = Date.now() - startTime;
      
      // API response should be fast
      if (authResponseTime > 0) {
        expect(authResponseTime).toBeLessThan(2000); // 2 second API response budget
        console.log(`Auth API response time: ${authResponseTime}ms`);
      }
      
      expect(totalAuthTime).toBeLessThan(5000); // Total auth flow under 5 seconds
      console.log(`Total authentication time: ${totalAuthTime}ms`);
    });

    test('should have efficient QVF scoring API performance', async ({ page }) => {
      await login(page, TestUsers.productOwner);
      await navigateTo(page, '/work-items');
      
      let qvfApiCalls: Array<{ url: string; responseTime: number; status: number }> = [];
      
      page.on('response', async (response) => {
        const url = response.url();
        if (url.includes('/qvf') || url.includes('/score') || url.includes('/work-items')) {
          qvfApiCalls.push({
            url,
            responseTime: response.timing()?.responseTime || 0,
            status: response.status()
          });
        }
      });
      
      // Look for QVF calculation trigger
      const calculateButton = page.locator('button:has-text("Calculate"), button:has-text("Score")').first();
      
      if (await calculateButton.isVisible({ timeout: 5000 })) {
        const startTime = Date.now();
        
        await calculateButton.click();
        await page.waitForTimeout(3000); // Wait for calculation
        
        const calculationTime = Date.now() - startTime;
        
        console.log(`QVF calculation completed in ${calculationTime}ms`);
        console.log(`QVF API calls:`, qvfApiCalls.map(call => ({
          url: call.url.split('/').pop(),
          time: `${call.responseTime}ms`,
          status: call.status
        })));
        
        // QVF calculation should complete reasonably quickly
        expect(calculationTime).toBeLessThan(10000); // 10 second budget for complex calculations
        
        // API responses should be efficient
        qvfApiCalls.forEach(call => {
          if (call.responseTime > 0) {
            expect(call.responseTime).toBeLessThan(5000); // 5 second per API call
          }
        });
      }
    });

    test('should handle concurrent API requests efficiently', async ({ browser }) => {
      // Create multiple browser contexts to simulate concurrent users
      const contexts = await Promise.all([
        browser.newContext(),
        browser.newContext(),
        browser.newContext()
      ]);
      
      const pages = await Promise.all(contexts.map(ctx => ctx.newPage()));
      
      try {
        // Track API performance across concurrent sessions
        const apiMetrics: Array<{ page: number; url: string; responseTime: number }> = [];
        
        pages.forEach((page, index) => {
          page.on('response', (response) => {
            const responseTime = response.timing()?.responseTime || 0;
            if (responseTime > 0 && response.url().includes('/api/')) {
              apiMetrics.push({
                page: index,
                url: response.url(),
                responseTime
              });
            }
          });
        });
        
        const startTime = Date.now();
        
        // Concurrent login operations
        await Promise.all([
          login(pages[0], TestUsers.executive),
          login(pages[1], TestUsers.productOwner),
          login(pages[2], TestUsers.scrumMaster)
        ]);
        
        const concurrentAuthTime = Date.now() - startTime;
        
        console.log(`Concurrent authentication completed in ${concurrentAuthTime}ms`);
        
        // Analyze API performance under load
        const avgResponseTime = apiMetrics.reduce((sum, metric) => sum + metric.responseTime, 0) / apiMetrics.length;
        const slowRequests = apiMetrics.filter(metric => metric.responseTime > 3000);
        
        console.log(`Average API response time under concurrent load: ${Math.round(avgResponseTime)}ms`);
        console.log(`Slow requests (>3s): ${slowRequests.length}/${apiMetrics.length}`);
        
        // Performance assertions for concurrent access
        expect(concurrentAuthTime).toBeLessThan(15000); // 15 seconds for 3 concurrent logins
        expect(slowRequests.length).toBeLessThan(apiMetrics.length * 0.2); // Less than 20% slow requests
        
      } finally {
        await Promise.all(contexts.map(ctx => ctx.close()));
      }
    });
  });

  test.describe('Resource Performance', () => {
    test('should have efficient resource loading', async ({ page }) => {
      const resourceMetrics = {
        totalSize: 0,
        imageSize: 0,
        jsSize: 0,
        cssSize: 0,
        requestCount: 0
      };
      
      page.on('response', async (response) => {
        const headers = response.headers();
        const contentLength = parseInt(headers['content-length'] || '0');
        const contentType = headers['content-type'] || '';
        
        resourceMetrics.totalSize += contentLength;
        resourceMetrics.requestCount++;
        
        if (contentType.includes('image/')) {
          resourceMetrics.imageSize += contentLength;
        } else if (contentType.includes('javascript') || response.url().endsWith('.js')) {
          resourceMetrics.jsSize += contentLength;
        } else if (contentType.includes('css') || response.url().endsWith('.css')) {
          resourceMetrics.cssSize += contentLength;
        }
      });
      
      await login(page, TestUsers.executive);
      await navigateTo(page, '/dashboard/executive');
      await waitForPageLoad(page);
      
      // Convert bytes to KB for logging
      const toKB = (bytes: number) => Math.round(bytes / 1024);
      
      console.log('Resource Loading Metrics:');
      console.log(`- Total Size: ${toKB(resourceMetrics.totalSize)}KB`);
      console.log(`- JavaScript: ${toKB(resourceMetrics.jsSize)}KB`);
      console.log(`- CSS: ${toKB(resourceMetrics.cssSize)}KB`);
      console.log(`- Images: ${toKB(resourceMetrics.imageSize)}KB`);
      console.log(`- Total Requests: ${resourceMetrics.requestCount}`);
      
      // Resource budget assertions
      expect(resourceMetrics.totalSize).toBeLessThan(5 * 1024 * 1024); // 5MB total
      expect(resourceMetrics.jsSize).toBeLessThan(2 * 1024 * 1024); // 2MB JS
      expect(resourceMetrics.cssSize).toBeLessThan(500 * 1024); // 500KB CSS
      expect(resourceMetrics.requestCount).toBeLessThan(50); // Max 50 requests
    });

    test('should efficiently handle large datasets', async ({ page }) => {
      await login(page, TestUsers.productOwner);
      
      // Mock large dataset response
      await page.route('**/api/v1/work-items', async (route) => {
        // Simulate delay for large dataset
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Mock large work items dataset
        const largeDataset = Array.from({ length: 100 }, (_, i) => ({
          id: `WI-${i.toString().padStart(3, '0')}`,
          title: `Work Item ${i}`,
          business_value: Math.floor(Math.random() * 10),
          technical_complexity: Math.floor(Math.random() * 10),
          story_points: Math.floor(Math.random() * 21),
          priority: ['High', 'Medium', 'Low'][Math.floor(Math.random() * 3)]
        }));
        
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(largeDataset)
        });
      });
      
      const startTime = Date.now();
      
      await navigateTo(page, '/work-items');
      await waitForPageLoad(page);
      
      // Wait for data to render
      await page.waitForTimeout(2000);
      
      const renderTime = Date.now() - startTime;
      
      console.log(`Large dataset rendered in ${renderTime}ms`);
      
      // Should handle large datasets efficiently
      expect(renderTime).toBeLessThan(8000); // 8 second budget for large datasets
    });
  });

  test.describe('Memory Performance', () => {
    test('should not have excessive memory usage', async ({ page }) => {
      await login(page, TestUsers.executive);
      
      // Navigate through multiple pages to test memory usage
      const routes = [
        '/dashboard/executive',
        '/work-items', 
        '/compare',
        '/dashboard/executive' // Return to start
      ];
      
      const memoryMeasurements: number[] = [];
      
      for (const route of routes) {
        try {
          await navigateTo(page, route);
          await waitForPageLoad(page);
          
          // Measure memory usage (if available)
          const metrics = await page.evaluate(() => {
            if ('memory' in performance) {
              return (performance as any).memory.usedJSHeapSize;
            }
            return 0;
          });
          
          if (metrics > 0) {
            memoryMeasurements.push(metrics);
            console.log(`Memory usage at ${route}: ${Math.round(metrics / 1024 / 1024)}MB`);
          }
          
          await page.waitForTimeout(1000);
        } catch {
          console.log(`Could not navigate to ${route}`);
        }
      }
      
      if (memoryMeasurements.length >= 2) {
        // Check for memory leaks (significant memory increase without release)
        const memoryIncrease = memoryMeasurements[memoryMeasurements.length - 1] - memoryMeasurements[0];
        const memoryIncreaseMB = memoryIncrease / 1024 / 1024;
        
        console.log(`Total memory increase: ${Math.round(memoryIncreaseMB)}MB`);
        
        // Should not have excessive memory growth during navigation
        expect(memoryIncreaseMB).toBeLessThan(50); // Less than 50MB increase
      }
    });
  });

  test.describe('User Interaction Performance', () => {
    test('should have responsive UI interactions', async ({ page }) => {
      await login(page, TestUsers.productOwner);
      await navigateTo(page, '/work-items');
      
      // Test click responsiveness
      const clickableElements = await page.locator('button, a, [role="button"]').all();
      
      if (clickableElements.length > 0) {
        const startTime = Date.now();
        
        await clickableElements[0].click();
        await page.waitForTimeout(100); // Small delay to measure response
        
        const responseTime = Date.now() - startTime;
        
        console.log(`UI interaction response time: ${responseTime}ms`);
        
        // UI should respond quickly to user interactions
        expect(responseTime).toBeLessThan(500); // 500ms for UI response
      }
    });

    test('should handle form input efficiently', async ({ page }) => {
      await login(page, TestUsers.productOwner);
      await navigateTo(page, '/work-items');
      
      // Look for form inputs
      const inputs = await page.locator('input[type="text"], input[type="number"], textarea').all();
      
      if (inputs.length > 0) {
        const testString = 'Performance test input';
        const startTime = Date.now();
        
        await inputs[0].fill(testString);
        
        const inputTime = Date.now() - startTime;
        
        console.log(`Form input response time: ${inputTime}ms`);
        
        // Form input should be responsive
        expect(inputTime).toBeLessThan(200); // 200ms for input response
      }
    });
  });

  test.describe('Network Performance', () => {
    test('should handle slow network conditions', async ({ page, context }) => {
      // Simulate slow network
      await context.route('**/*', async (route) => {
        // Add artificial delay
        await new Promise(resolve => setTimeout(resolve, 100));
        await route.continue();
      });
      
      const startTime = Date.now();
      
      await login(page, TestUsers.executive);
      await navigateTo(page, '/dashboard/executive');
      
      const loadTime = Date.now() - startTime;
      
      console.log(`Load time with simulated slow network: ${loadTime}ms`);
      
      // Should still be usable on slow networks (though slower)
      expect(loadTime).toBeLessThan(15000); // 15 seconds on slow network
    });

    test('should handle network errors gracefully', async ({ page }) => {
      await login(page, TestUsers.productOwner);
      
      // Simulate network failures for API calls
      await page.route('**/api/**', async (route) => {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ error: 'Network error' })
        });
      });
      
      const startTime = Date.now();
      
      await navigateTo(page, '/work-items');
      await page.waitForTimeout(3000); // Wait for error handling
      
      const errorHandlingTime = Date.now() - startTime;
      
      console.log(`Error handling time: ${errorHandlingTime}ms`);
      
      // Should handle errors efficiently
      expect(errorHandlingTime).toBeLessThan(10000); // 10 seconds to handle errors
      
      // Page should still be responsive
      const pageTitle = await page.title();
      expect(pageTitle).toBeTruthy();
    });
  });
});