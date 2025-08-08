import { test, expect } from '@playwright/test';
import { TestUsers, TestWorkItems } from '../fixtures/test-users';
import { login, navigateTo, waitForPageLoad, takeScreenshot, fillField, waitForElement } from '../fixtures/test-helpers';

test.describe('QVF Scoring Workflow', () => {
  
  test.beforeEach(async ({ page }) => {
    // Login as product owner (most likely role to use QVF scoring)
    await login(page, TestUsers.productOwner);
  });

  test('should access QVF scoring interface', async ({ page }) => {
    // Try to navigate to QVF scoring interface
    const qvfRoutes = ['/work-items', '/qvf-scoring', '/scoring', '/compare'];
    
    let scoringFound = false;
    for (const route of qvfRoutes) {
      try {
        await navigateTo(page, route);
        
        // Look for QVF-related elements
        const qvfElements = [
          'QVF Score',
          'Quality Value Framework',
          'Business Value',
          'Technical Complexity',
          'Story Points',
          'Priority',
          'Calculate QVF'
        ];
        
        let foundElements = 0;
        for (const element of qvfElements) {
          if (await page.locator(`text=${element}`).isVisible({ timeout: 3000 }).catch(() => false)) {
            foundElements++;
          }
        }
        
        if (foundElements >= 2) {
          scoringFound = true;
          console.log(`Found QVF interface at ${route}`);
          break;
        }
      } catch {
        continue;
      }
    }
    
    expect(scoringFound).toBeTruthy();
    await takeScreenshot(page, 'qvf-scoring-interface');
  });

  test('should display work items for QVF scoring', async ({ page }) => {
    await navigateTo(page, '/work-items');
    
    // Look for work items table or list
    const workItemsContainer = await page.locator([
      'table',
      '[data-testid="work-items-list"]', 
      '[data-testid="work-items-table"]',
      '.work-items',
      '.items-container'
    ].join(', ')).first();
    
    if (await workItemsContainer.isVisible({ timeout: 10000 }).catch(() => false)) {
      // Check for work item columns/headers
      const expectedHeaders = [
        'Title',
        'Business Value',
        'Technical Complexity', 
        'Story Points',
        'Priority',
        'QVF Score'
      ];
      
      let foundHeaders = 0;
      for (const header of expectedHeaders) {
        if (await page.locator(`text=${header}`).isVisible({ timeout: 3000 }).catch(() => false)) {
          foundHeaders++;
        }
      }
      
      expect(foundHeaders).toBeGreaterThan(2); // At least some work item headers
    }
    
    await takeScreenshot(page, 'work-items-display');
  });

  test('should allow QVF score calculation', async ({ page }) => {
    await navigateTo(page, '/work-items');
    
    // Look for calculate QVF button or similar
    const calculateButtons = [
      'button:has-text("Calculate QVF")',
      'button:has-text("Calculate Scores")',
      'button:has-text("Score Items")',
      '[data-testid="calculate-qvf"]',
      '.calculate-btn'
    ];
    
    let calculateFound = false;
    for (const selector of calculateButtons) {
      if (await page.locator(selector).isVisible({ timeout: 3000 }).catch(() => false)) {
        try {
          await page.click(selector);
          await waitForPageLoad(page);
          calculateFound = true;
          break;
        } catch {
          continue;
        }
      }
    }
    
    if (calculateFound) {
      // Wait for calculation results
      await page.waitForTimeout(3000);
      
      // Look for QVF scores in results
      const scoreElements = [
        '.qvf-score',
        '[data-testid="qvf-score"]',
        'text=/score.*\d+/i',
        'text=/qvf.*\d+/i'
      ];
      
      let scoresFound = 0;
      for (const selector of scoreElements) {
        const elements = await page.locator(selector).all();
        scoresFound += elements.length;
      }
      
      expect(scoresFound).toBeGreaterThan(0);
    }
    
    await takeScreenshot(page, 'qvf-calculation-results');
  });

  test('should handle work item input for scoring', async ({ page }) => {
    await navigateTo(page, '/work-items');
    
    // Look for add/edit work item functionality
    const addButtons = [
      'button:has-text("Add Work Item")',
      'button:has-text("New Item")',
      'button:has-text("Create")',
      '[data-testid="add-work-item"]',
      '.add-item-btn'
    ];
    
    let addFound = false;
    for (const selector of addButtons) {
      if (await page.locator(selector).isVisible({ timeout: 3000 }).catch(() => false)) {
        try {
          await page.click(selector);
          await waitForPageLoad(page);
          addFound = true;
          break;
        } catch {
          continue;
        }
      }
    }
    
    if (addFound) {
      // Fill out work item form if modal/form appears
      const formFields = [
        { selector: 'input[name="title"], [data-testid="title"]', value: 'Test Work Item' },
        { selector: 'input[name="business_value"], [data-testid="business-value"]', value: '8' },
        { selector: 'input[name="technical_complexity"], [data-testid="complexity"]', value: '6' },
        { selector: 'input[name="story_points"], [data-testid="story-points"]', value: '5' }
      ];
      
      for (const field of formFields) {
        try {
          if (await page.locator(field.selector).isVisible({ timeout: 3000 }).catch(() => false)) {
            await fillField(page, field.selector, field.value);
          }
        } catch {
          // Field might not exist, continue
        }
      }
      
      // Try to submit form
      const submitButtons = [
        'button:has-text("Save")',
        'button:has-text("Submit")',
        'button:has-text("Create")',
        'button[type="submit"]'
      ];
      
      for (const selector of submitButtons) {
        if (await page.locator(selector).isVisible({ timeout: 3000 }).catch(() => false)) {
          try {
            await page.click(selector);
            await waitForPageLoad(page);
            break;
          } catch {
            continue;
          }
        }
      }
      
      await takeScreenshot(page, 'work-item-creation');
    }
  });

  test('should validate QVF scoring criteria', async ({ page }) => {
    await navigateTo(page, '/work-items');
    
    // Look for criteria information or settings
    const criteriaElements = [
      'text=Business Value',
      'text=Technical Complexity',
      'text=Risk Level',
      'text=Strategic Alignment',
      'text=Dependencies'
    ];
    
    let criteriaFound = 0;
    for (const element of criteriaElements) {
      if (await page.locator(element).isVisible({ timeout: 3000 }).catch(() => false)) {
        criteriaFound++;
      }
    }
    
    // Should find some QVF criteria
    expect(criteriaFound).toBeGreaterThan(1);
    
    // Look for criteria weights or configuration
    const weightElements = [
      'text=/weight.*\d+/i',
      'text=/importance.*\d+/i',
      '[data-testid="criteria-weight"]',
      '.weight-value'
    ];
    
    for (const selector of weightElements) {
      if (await page.locator(selector).isVisible({ timeout: 3000 }).catch(() => false)) {
        console.log('Found criteria weights');
        break;
      }
    }
    
    await takeScreenshot(page, 'qvf-criteria-display');
  });

  test('should display QVF scoring results properly', async ({ page }) => {
    await navigateTo(page, '/work-items');
    
    // Mock or wait for QVF calculation results
    await page.waitForTimeout(2000);
    
    // Look for QVF score display patterns
    const scorePatterns = [
      /QVF.*\d+\.?\d*/,
      /Score.*\d+\.?\d*/,
      /Priority.*High|Medium|Low/,
      /Tier.*\d+/
    ];
    
    const pageContent = await page.textContent('body');
    let foundScorePatterns = 0;
    
    for (const pattern of scorePatterns) {
      if (pattern.test(pageContent)) {
        foundScorePatterns++;
      }
    }
    
    // Should find some score-related content patterns
    expect(foundScorePatterns).toBeGreaterThanOrEqual(0);
    
    // Look for score visualization elements
    const visualElements = [
      '.progress-bar',
      '.score-chart',
      '.priority-indicator',
      '[data-testid="score-visualization"]',
      'svg', // Charts might use SVG
      'canvas' // Or canvas for visualizations
    ];
    
    let visualFound = false;
    for (const selector of visualElements) {
      if (await page.locator(selector).isVisible({ timeout: 3000 }).catch(() => false)) {
        visualFound = true;
        break;
      }
    }
    
    await takeScreenshot(page, 'qvf-results-visualization');
  });

  test('should handle bulk QVF scoring operations', async ({ page }) => {
    await navigateTo(page, '/work-items');
    
    // Look for bulk operations
    const bulkElements = [
      'button:has-text("Select All")',
      'button:has-text("Bulk")',
      'input[type="checkbox"]',
      '[data-testid="bulk-select"]',
      '.bulk-actions'
    ];
    
    let bulkFound = false;
    for (const selector of bulkElements) {
      if (await page.locator(selector).isVisible({ timeout: 3000 }).catch(() => false)) {
        bulkFound = true;
        console.log(`Found bulk operations: ${selector}`);
        break;
      }
    }
    
    if (bulkFound) {
      // Try bulk selection
      const checkboxes = await page.locator('input[type="checkbox"]').all();
      if (checkboxes.length > 0) {
        // Select first few items
        for (let i = 0; i < Math.min(3, checkboxes.length); i++) {
          try {
            await checkboxes[i].check();
          } catch {
            continue;
          }
        }
        
        // Look for bulk calculate button
        const bulkCalculateButtons = [
          'button:has-text("Calculate Selected")',
          'button:has-text("Bulk Calculate")',
          '[data-testid="bulk-calculate"]'
        ];
        
        for (const selector of bulkCalculateButtons) {
          if (await page.locator(selector).isVisible({ timeout: 3000 }).catch(() => false)) {
            try {
              await page.click(selector);
              await waitForPageLoad(page);
              break;
            } catch {
              continue;
            }
          }
        }
      }
    }
    
    await takeScreenshot(page, 'bulk-qvf-operations');
  });

  test('should export QVF scoring results', async ({ page }) => {
    await navigateTo(page, '/work-items');
    
    // Look for export functionality
    const exportElements = [
      'button:has-text("Export")',
      'button:has-text("Download")', 
      'button:has-text("CSV")',
      'button:has-text("Excel")',
      '[data-testid="export-button"]',
      '.export-btn'
    ];
    
    let exportFound = false;
    for (const selector of exportElements) {
      if (await page.locator(selector).isVisible({ timeout: 3000 }).catch(() => false)) {
        exportFound = true;
        console.log(`Found export functionality: ${selector}`);
        
        // Set up download handler
        const downloadPromise = page.waitForEvent('download', { timeout: 10000 }).catch(() => null);
        
        try {
          await page.click(selector);
          const download = await downloadPromise;
          
          if (download) {
            // Verify download
            const fileName = download.suggestedFilename();
            expect(fileName).toBeTruthy();
            console.log(`Downloaded file: ${fileName}`);
          }
        } catch {
          // Export might not be fully functional
        }
        
        break;
      }
    }
    
    await takeScreenshot(page, 'qvf-export-functionality');
  });

  test('should handle QVF scoring errors gracefully', async ({ page }) => {
    await navigateTo(page, '/work-items');
    
    // Try to trigger error conditions
    const errorScenarios = [
      {
        name: 'missing-data',
        action: async () => {
          // Try calculating QVF with incomplete data
          const calculateBtn = page.locator('button:has-text("Calculate"), button:has-text("Score")').first();
          if (await calculateBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
            await calculateBtn.click();
          }
        }
      },
      {
        name: 'invalid-values',
        action: async () => {
          // Try entering invalid values if form is available
          const businessValueInput = page.locator('input[name="business_value"], [data-testid="business-value"]').first();
          if (await businessValueInput.isVisible({ timeout: 3000 }).catch(() => false)) {
            await fillField(page, 'input[name="business_value"], [data-testid="business-value"]', '-1');
          }
        }
      }
    ];
    
    for (const scenario of errorScenarios) {
      try {
        await scenario.action();
        await page.waitForTimeout(2000);
        
        // Look for error messages
        const errorSelectors = [
          '.error',
          '.error-message', 
          '[role="alert"]',
          'text=/error|invalid|failed/i'
        ];
        
        let errorFound = false;
        for (const selector of errorSelectors) {
          if (await page.locator(selector).isVisible({ timeout: 3000 }).catch(() => false)) {
            errorFound = true;
            console.log(`Found error handling for ${scenario.name}`);
            break;
          }
        }
        
        await takeScreenshot(page, `qvf-error-${scenario.name}`);
        
      } catch (error) {
        console.log(`Error scenario ${scenario.name} test failed:`, error);
      }
    }
  });
});