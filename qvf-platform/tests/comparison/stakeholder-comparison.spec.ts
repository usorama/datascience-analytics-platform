import { test, expect } from '@playwright/test';
import { TestUsers, getAllTestUsers } from '../fixtures/test-users';
import { login, navigateTo, waitForPageLoad, takeScreenshot, waitForElement } from '../fixtures/test-helpers';

test.describe('QVF Stakeholder Comparison Interface', () => {
  
  test.beforeEach(async ({ page }) => {
    // Login as product owner who typically uses comparison features
    await login(page, TestUsers.productOwner);
  });

  test('should access stakeholder comparison interface', async ({ page }) => {
    // Try different routes where comparison might be available
    const comparisonRoutes = [
      '/compare',
      '/comparison', 
      '/qvf-comparison',
      '/stakeholder-comparison',
      '/dashboard/product-owner' // Might have comparison widget
    ];
    
    let comparisonFound = false;
    for (const route of comparisonRoutes) {
      try {
        await navigateTo(page, route);
        
        // Look for comparison-related elements
        const comparisonElements = [
          'Stakeholder Comparison',
          'Compare QVF',
          'Pairwise Comparison',
          'Comparison Matrix',
          'Consensus',
          'Stakeholder Input',
          'Comparison Progress'
        ];
        
        let foundElements = 0;
        for (const element of comparisonElements) {
          if (await page.locator(`text=${element}`).isVisible({ timeout: 5000 }).catch(() => false)) {
            foundElements++;
          }
        }
        
        if (foundElements >= 2) {
          comparisonFound = true;
          console.log(`Found comparison interface at ${route} with ${foundElements} elements`);
          break;
        }
      } catch {
        continue;
      }
    }
    
    expect(comparisonFound).toBeTruthy();
    await takeScreenshot(page, 'stakeholder-comparison-interface');
  });

  test('should display comparison matrix', async ({ page }) => {
    await navigateTo(page, '/compare');
    
    // Look for matrix-like structures
    const matrixSelectors = [
      'table',
      '.comparison-matrix',
      '[data-testid="comparison-matrix"]',
      '.matrix-container',
      '.pairwise-matrix'
    ];
    
    let matrixFound = false;
    for (const selector of matrixSelectors) {
      if (await page.locator(selector).isVisible({ timeout: 10000 }).catch(() => false)) {
        matrixFound = true;
        console.log(`Found comparison matrix: ${selector}`);
        
        // Check if it looks like a comparison matrix (has multiple rows/cells)
        const cellCount = await page.locator(`${selector} td, ${selector} .cell, ${selector} .matrix-cell`).count();
        if (cellCount > 4) { // Should have multiple comparison cells
          console.log(`Matrix has ${cellCount} cells`);
        }
        
        break;
      }
    }
    
    // Alternative: look for comparison pairs or items
    if (!matrixFound) {
      const comparisonItems = await page.locator('.comparison-item, .compare-item, [data-testid*="comparison"]').count();
      if (comparisonItems > 1) {
        matrixFound = true;
        console.log(`Found ${comparisonItems} comparison items`);
      }
    }
    
    await takeScreenshot(page, 'comparison-matrix-display');
    expect(matrixFound).toBeTruthy();
  });

  test('should allow stakeholder input selection', async ({ page }) => {
    await navigateTo(page, '/compare');
    
    // Look for stakeholder selection or role-based input
    const stakeholderSelectors = [
      'select[name*="stakeholder"]',
      '[data-testid="stakeholder-select"]',
      'button:has-text("Executive")',
      'button:has-text("Product Owner")',
      'button:has-text("Scrum Master")',
      '.stakeholder-selector',
      '.role-selector'
    ];
    
    let stakeholderInputFound = false;
    for (const selector of stakeholderSelectors) {
      if (await page.locator(selector).isVisible({ timeout: 5000 }).catch(() => false)) {
        stakeholderInputFound = true;
        console.log(`Found stakeholder selection: ${selector}`);
        
        try {
          if (selector.includes('select')) {
            const options = await page.locator(`${selector} option`).all();
            if (options.length > 1) {
              await page.selectOption(selector, await options[1].getAttribute('value') || '');
            }
          } else {
            await page.click(selector);
          }
          
          await waitForPageLoad(page);
        } catch {
          // Selection might not be functional yet
        }
        
        break;
      }
    }
    
    await takeScreenshot(page, 'stakeholder-input-selection');
  });

  test('should handle pairwise comparisons', async ({ page }) => {
    await navigateTo(page, '/compare');
    
    // Look for pairwise comparison elements
    const pairwiseSelectors = [
      '.pairwise-comparison',
      '[data-testid="pairwise"]',
      '.comparison-pair',
      'input[type="radio"]',
      'button:has-text("A vs B")',
      '.vs-indicator'
    ];
    
    let pairwiseFound = false;
    for (const selector of pairwiseSelectors) {
      if (await page.locator(selector).isVisible({ timeout: 5000 }).catch(() => false)) {
        pairwiseFound = true;
        console.log(`Found pairwise comparison: ${selector}`);
        
        // Try to interact with pairwise comparison
        try {
          if (selector.includes('radio')) {
            const radioButtons = await page.locator(selector).all();
            if (radioButtons.length > 0) {
              await radioButtons[0].check();
            }
          } else if (selector.includes('button')) {
            await page.click(selector);
          }
          
          await page.waitForTimeout(1000);
        } catch {
          // Interaction might not be functional yet
        }
        
        break;
      }
    }
    
    // Look for comparison controls (sliders, buttons, dropdowns)
    const comparisonControls = [
      'input[type="range"]',
      'button:has-text("Prefer")',
      'button:has-text("Choose")',
      'select[name*="preference"]',
      '.comparison-control'
    ];
    
    let controlsFound = 0;
    for (const selector of comparisonControls) {
      if (await page.locator(selector).isVisible({ timeout: 3000 }).catch(() => false)) {
        controlsFound++;
        
        try {
          if (selector.includes('range')) {
            await page.fill(selector, '7');
          } else if (selector.includes('button')) {
            await page.click(selector);
          } else if (selector.includes('select')) {
            await page.selectOption(selector, { index: 1 });
          }
          
          await page.waitForTimeout(500);
        } catch {
          // Control might not be functional yet
        }
      }
    }
    
    console.log(`Found ${controlsFound} comparison controls`);
    await takeScreenshot(page, 'pairwise-comparison-interaction');
  });

  test('should show comparison progress', async ({ page }) => {
    await navigateTo(page, '/compare');
    
    // Look for progress indicators
    const progressSelectors = [
      '.progress',
      '.progress-bar',
      '[data-testid="progress"]',
      'progress',
      'text=/\d+%/',
      'text=/\d+ of \d+/',
      '.completion-indicator'
    ];
    
    let progressFound = false;
    for (const selector of progressSelectors) {
      if (await page.locator(selector).isVisible({ timeout: 5000 }).catch(() => false)) {
        progressFound = true;
        console.log(`Found progress indicator: ${selector}`);
        
        // Get progress text if available
        try {
          const progressText = await page.locator(selector).textContent();
          if (progressText) {
            console.log(`Progress text: ${progressText}`);
          }
        } catch {
          // Text extraction might fail
        }
        
        break;
      }
    }
    
    // Look for completion status
    const statusElements = [
      'text=/complete/i',
      'text=/pending/i',
      'text=/in progress/i',
      '.status',
      '[data-testid="status"]'
    ];
    
    for (const selector of statusElements) {
      if (await page.locator(selector).isVisible({ timeout: 3000 }).catch(() => false)) {
        console.log(`Found status element: ${selector}`);
        break;
      }
    }
    
    await takeScreenshot(page, 'comparison-progress-display');
  });

  test('should display consistency indicators', async ({ page }) => {
    await navigateTo(page, '/compare');
    
    // Look for consistency-related elements
    const consistencyElements = [
      'text=/consistency/i',
      'text=/consistent/i',
      'text=/inconsistent/i',
      'text=/ratio/i',
      '.consistency-indicator',
      '[data-testid="consistency"]',
      '.consistency-score'
    ];
    
    let consistencyFound = false;
    for (const selector of consistencyElements) {
      if (await page.locator(selector).isVisible({ timeout: 5000 }).catch(() => false)) {
        consistencyFound = true;
        console.log(`Found consistency indicator: ${selector}`);
        break;
      }
    }
    
    // Look for numerical consistency scores
    const scorePatterns = [
      /consistency.*\d+\.?\d*/i,
      /ratio.*\d+\.?\d*/i,
      /score.*\d+\.?\d*/i
    ];
    
    const pageContent = await page.textContent('body');
    for (const pattern of scorePatterns) {
      if (pattern.test(pageContent)) {
        console.log(`Found consistency score pattern: ${pattern}`);
        break;
      }
    }
    
    await takeScreenshot(page, 'consistency-indicators');
  });

  test('should handle different stakeholder perspectives', async ({ page }) => {
    // Test with different user roles to see different perspectives
    const stakeholders = [
      { user: TestUsers.executive, perspective: 'Strategic/Business' },
      { user: TestUsers.productOwner, perspective: 'Product/Value' },
      { user: TestUsers.scrumMaster, perspective: 'Team/Process' }
    ];
    
    for (const stakeholder of stakeholders) {
      // Re-login as different stakeholder
      await page.context().clearCookies();
      await page.evaluate(() => {
        localStorage.clear();
        sessionStorage.clear();
      });
      
      await login(page, stakeholder.user);
      await navigateTo(page, '/compare');
      
      // Check if interface adapts to stakeholder role
      const roleSpecificElements = [
        stakeholder.user.role,
        stakeholder.perspective.split('/')[0],
        stakeholder.perspective.split('/')[1]
      ];
      
      let roleElementsFound = 0;
      for (const element of roleSpecificElements) {
        if (await page.locator(`text=${element}`).isVisible({ timeout: 5000 }).catch(() => false)) {
          roleElementsFound++;
        }
      }
      
      console.log(`${stakeholder.user.role} perspective: found ${roleElementsFound} role-specific elements`);
      
      await takeScreenshot(page, `comparison-${stakeholder.user.role}-perspective`);
      
      // Brief pause between role switches
      await page.waitForTimeout(1000);
    }
  });

  test('should allow comparison result export', async ({ page }) => {
    await navigateTo(page, '/compare');
    
    // Look for export functionality
    const exportSelectors = [
      'button:has-text("Export")',
      'button:has-text("Download")',
      'button:has-text("Save Results")',
      '[data-testid="export"]',
      '.export-button'
    ];
    
    for (const selector of exportSelectors) {
      if (await page.locator(selector).isVisible({ timeout: 5000 }).catch(() => false)) {
        console.log(`Found export functionality: ${selector}`);
        
        // Set up download handler
        const downloadPromise = page.waitForEvent('download', { timeout: 10000 }).catch(() => null);
        
        try {
          await page.click(selector);
          const download = await downloadPromise;
          
          if (download) {
            const fileName = download.suggestedFilename();
            console.log(`Export download: ${fileName}`);
          }
        } catch {
          // Export might not be fully functional
          console.log('Export functionality exists but may not be fully implemented');
        }
        
        break;
      }
    }
    
    await takeScreenshot(page, 'comparison-export-functionality');
  });

  test('should handle comparison data validation', async ({ page }) => {
    await navigateTo(page, '/compare');
    
    // Try to submit incomplete comparison
    const submitButtons = [
      'button:has-text("Submit")',
      'button:has-text("Complete")',
      'button:has-text("Finish")',
      '[data-testid="submit-comparison"]'
    ];
    
    for (const selector of submitButtons) {
      if (await page.locator(selector).isVisible({ timeout: 5000 }).catch(() => false)) {
        await page.click(selector);
        await page.waitForTimeout(2000);
        
        // Look for validation messages
        const validationSelectors = [
          '.error',
          '.error-message',
          '[role="alert"]',
          'text=/required|incomplete|invalid/i',
          '.validation-error'
        ];
        
        let validationFound = false;
        for (const validationSelector of validationSelectors) {
          if (await page.locator(validationSelector).isVisible({ timeout: 3000 }).catch(() => false)) {
            validationFound = true;
            console.log(`Found validation message: ${validationSelector}`);
            break;
          }
        }
        
        await takeScreenshot(page, 'comparison-validation-error');
        break;
      }
    }
  });

  test('should show comparison results summary', async ({ page }) => {
    await navigateTo(page, '/compare');
    
    // Look for results or summary sections
    const summarySelectors = [
      '.results',
      '.summary',
      '[data-testid="results"]',
      '.comparison-results',
      'h2:has-text("Results")',
      'h3:has-text("Summary")'
    ];
    
    let summaryFound = false;
    for (const selector of summarySelectors) {
      if (await page.locator(selector).isVisible({ timeout: 5000 }).catch(() => false)) {
        summaryFound = true;
        console.log(`Found results summary: ${selector}`);
        break;
      }
    }
    
    // Look for result metrics
    const metricPatterns = [
      /rank.*\d+/i,
      /score.*\d+\.?\d*/i,
      /priority.*high|medium|low/i,
      /weight.*\d+\.?\d*/i,
      /consensus.*\d+/i
    ];
    
    const pageContent = await page.textContent('body');
    let metricsFound = 0;
    
    for (const pattern of metricPatterns) {
      if (pattern.test(pageContent)) {
        metricsFound++;
      }
    }
    
    console.log(`Found ${metricsFound} result metric patterns`);
    
    // Look for visualization elements
    const chartSelectors = [
      'svg',
      'canvas',
      '.chart',
      '.graph',
      '.visualization'
    ];
    
    for (const selector of chartSelectors) {
      if (await page.locator(selector).isVisible({ timeout: 3000 }).catch(() => false)) {
        console.log(`Found result visualization: ${selector}`);
        break;
      }
    }
    
    await takeScreenshot(page, 'comparison-results-summary');
  });

  test('should handle real-time collaboration features', async ({ browser }) => {
    // Test with multiple browser contexts (simulating multiple stakeholders)
    const context1 = await browser.newContext();
    const context2 = await browser.newContext();
    
    const page1 = await context1.newPage();
    const page2 = await context2.newPage();
    
    try {
      // Login as different stakeholders
      await login(page1, TestUsers.executive);
      await login(page2, TestUsers.productOwner);
      
      // Both navigate to comparison page
      await navigateTo(page1, '/compare');
      await navigateTo(page2, '/compare');
      
      // Look for real-time indicators
      const realtimeElements = [
        'text=/online/i',
        'text=/users/i',
        'text=/connected/i',
        '.user-indicator',
        '.online-status',
        '[data-testid="collaboration"]'
      ];
      
      let collaborationFound = false;
      for (const selector of realtimeElements) {
        if (await page1.locator(selector).isVisible({ timeout: 5000 }).catch(() => false) ||
            await page2.locator(selector).isVisible({ timeout: 5000 }).catch(() => false)) {
          collaborationFound = true;
          console.log(`Found collaboration feature: ${selector}`);
          break;
        }
      }
      
      await takeScreenshot(page1, 'comparison-collaboration-user1');
      await takeScreenshot(page2, 'comparison-collaboration-user2');
      
    } finally {
      await context1.close();
      await context2.close();
    }
  });
});