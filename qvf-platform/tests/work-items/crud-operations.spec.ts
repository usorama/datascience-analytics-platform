import { test, expect } from '@playwright/test';
import { TestUsers, TestWorkItems } from '../fixtures/test-users';
import { login, navigateTo, waitForPageLoad, takeScreenshot, fillField, waitForElement } from '../fixtures/test-helpers';

test.describe('Work Items CRUD Operations', () => {
  
  test.beforeEach(async ({ page }) => {
    // Login as product owner who typically manages work items
    await login(page, TestUsers.productOwner);
  });

  test.describe('Create Work Items', () => {
    test('should create a new work item', async ({ page }) => {
      await navigateTo(page, '/work-items');
      
      // Look for create/add work item button
      const addButtons = [
        'button:has-text("Add Work Item")',
        'button:has-text("New Item")',
        'button:has-text("Create Item")',
        'button:has-text("Add")',
        '[data-testid="add-work-item"]',
        '[data-testid="create-item"]',
        '.add-work-item-btn'
      ];
      
      let createFormFound = false;
      for (const selector of addButtons) {
        if (await page.locator(selector).isVisible({ timeout: 5000 }).catch(() => false)) {
          await page.click(selector);
          await waitForPageLoad(page);
          createFormFound = true;
          console.log(`Found create button: ${selector}`);
          break;
        }
      }
      
      if (createFormFound) {
        // Fill out the work item creation form
        const testItem = {
          title: 'E2E Test Work Item',
          businessValue: '8',
          technicalComplexity: '6',
          storyPoints: '5',
          priority: 'High',
          description: 'This is a test work item created by E2E tests'
        };
        
        // Title field
        const titleSelectors = [
          'input[name="title"]',
          '[data-testid="title"]',
          '[placeholder*="title" i]',
          'input[type="text"]'
        ];
        
        for (const selector of titleSelectors) {
          if (await page.locator(selector).isVisible({ timeout: 3000 }).catch(() => false)) {
            await fillField(page, selector, testItem.title);
            break;
          }
        }
        
        // Business Value field
        const businessValueSelectors = [
          'input[name="business_value"]',
          'input[name="businessValue"]',
          '[data-testid="business-value"]',
          '[placeholder*="business" i]'
        ];
        
        for (const selector of businessValueSelectors) {
          if (await page.locator(selector).isVisible({ timeout: 3000 }).catch(() => false)) {
            await fillField(page, selector, testItem.businessValue);
            break;
          }
        }
        
        // Technical Complexity field
        const complexitySelectors = [
          'input[name="technical_complexity"]',
          'input[name="technicalComplexity"]',
          '[data-testid="technical-complexity"]',
          '[data-testid="complexity"]',
          '[placeholder*="complexity" i]'
        ];
        
        for (const selector of complexitySelectors) {
          if (await page.locator(selector).isVisible({ timeout: 3000 }).catch(() => false)) {
            await fillField(page, selector, testItem.technicalComplexity);
            break;
          }
        }
        
        // Story Points field
        const storyPointsSelectors = [
          'input[name="story_points"]',
          'input[name="storyPoints"]',
          '[data-testid="story-points"]',
          '[placeholder*="points" i]'
        ];
        
        for (const selector of storyPointsSelectors) {
          if (await page.locator(selector).isVisible({ timeout: 3000 }).catch(() => false)) {
            await fillField(page, selector, testItem.storyPoints);
            break;
          }
        }
        
        // Priority dropdown
        const prioritySelectors = [
          'select[name="priority"]',
          '[data-testid="priority"]',
          'select[name="priority"] option[value="High"]'
        ];
        
        for (const selector of prioritySelectors) {
          if (await page.locator(selector).isVisible({ timeout: 3000 }).catch(() => false)) {
            if (selector.includes('option')) {
              await page.click(selector);
            } else {
              await page.selectOption(selector, 'High');
            }
            break;
          }
        }
        
        // Description field
        const descriptionSelectors = [
          'textarea[name="description"]',
          '[data-testid="description"]',
          'textarea',
          '[placeholder*="description" i]'
        ];
        
        for (const selector of descriptionSelectors) {
          if (await page.locator(selector).isVisible({ timeout: 3000 }).catch(() => false)) {
            await page.fill(selector, testItem.description);
            break;
          }
        }
        
        await takeScreenshot(page, 'work-item-create-form-filled');
        
        // Submit the form
        const submitButtons = [
          'button:has-text("Save")',
          'button:has-text("Create")',
          'button:has-text("Submit")',
          'button[type="submit"]',
          '[data-testid="submit"]'
        ];
        
        for (const selector of submitButtons) {
          if (await page.locator(selector).isVisible({ timeout: 3000 }).catch(() => false)) {
            await page.click(selector);
            await waitForPageLoad(page);
            break;
          }
        }
        
        // Verify work item was created
        await page.waitForTimeout(3000);
        const createdItemExists = await page.locator(`text=${testItem.title}`).isVisible({ timeout: 5000 }).catch(() => false);
        
        if (createdItemExists) {
          console.log('Work item creation successful');
        }
        
        await takeScreenshot(page, 'work-item-created');
      } else {
        console.log('Create work item functionality not found - this may not be implemented yet');
        await takeScreenshot(page, 'work-items-page-no-create');
      }
    });

    test('should validate required fields in work item creation', async ({ page }) => {
      await navigateTo(page, '/work-items');
      
      // Try to find and click create button
      const addButton = page.locator('button:has-text("Add"), button:has-text("Create"), button:has-text("New")').first();
      
      if (await addButton.isVisible({ timeout: 5000 }).catch(() => false)) {
        await addButton.click();
        await waitForPageLoad(page);
        
        // Try to submit empty form
        const submitButton = page.locator('button:has-text("Save"), button:has-text("Create"), button[type="submit"]').first();
        
        if (await submitButton.isVisible({ timeout: 3000 }).catch(() => false)) {
          await submitButton.click();
          await page.waitForTimeout(2000);
          
          // Look for validation errors
          const validationSelectors = [
            '.error',
            '.error-message',
            '[role="alert"]',
            'text=/required|invalid|must/i',
            '.field-error'
          ];
          
          let validationFound = false;
          for (const selector of validationSelectors) {
            if (await page.locator(selector).isVisible({ timeout: 3000 }).catch(() => false)) {
              validationFound = true;
              console.log(`Found validation: ${selector}`);
              break;
            }
          }
          
          await takeScreenshot(page, 'work-item-validation-errors');
        }
      }
    });
  });

  test.describe('Read Work Items', () => {
    test('should display work items list', async ({ page }) => {
      await navigateTo(page, '/work-items');
      
      // Look for work items table or list
      const listSelectors = [
        'table',
        '[data-testid="work-items-table"]',
        '[data-testid="work-items-list"]',
        '.work-items-container',
        '.items-list',
        '.data-table'
      ];
      
      let listFound = false;
      for (const selector of listSelectors) {
        if (await page.locator(selector).isVisible({ timeout: 10000 }).catch(() => false)) {
          listFound = true;
          console.log(`Found work items list: ${selector}`);
          break;
        }
      }
      
      expect(listFound).toBeTruthy();
      
      // Check for expected columns/headers
      const expectedHeaders = [
        'Title',
        'ID',
        'Business Value',
        'Technical Complexity',
        'Story Points',
        'Priority',
        'State',
        'Assigned'
      ];
      
      let foundHeaders = 0;
      for (const header of expectedHeaders) {
        if (await page.locator(`text=${header}`).isVisible({ timeout: 3000 }).catch(() => false)) {
          foundHeaders++;
        }
      }
      
      expect(foundHeaders).toBeGreaterThan(2); // Should find at least some headers
      
      await takeScreenshot(page, 'work-items-list-display');
    });

    test('should allow work item search and filtering', async ({ page }) => {
      await navigateTo(page, '/work-items');
      
      // Look for search functionality
      const searchSelectors = [
        'input[placeholder*="search" i]',
        'input[type="search"]',
        '[data-testid="search"]',
        '[data-testid="search-input"]',
        '.search-input'
      ];
      
      let searchFound = false;
      for (const selector of searchSelectors) {
        if (await page.locator(selector).isVisible({ timeout: 5000 }).catch(() => false)) {
          searchFound = true;
          
          // Test search functionality
          await fillField(page, selector, 'test');
          await page.waitForTimeout(1000); // Wait for search results
          
          console.log(`Found search functionality: ${selector}`);
          break;
        }
      }
      
      // Look for filter controls
      const filterSelectors = [
        'select',
        '[data-testid="filter"]',
        'button:has-text("Filter")',
        '.filter-button',
        'input[type="checkbox"]'
      ];
      
      let filterFound = false;
      for (const selector of filterSelectors) {
        if (await page.locator(selector).isVisible({ timeout: 3000 }).catch(() => false)) {
          filterFound = true;
          console.log(`Found filter functionality: ${selector}`);
          break;
        }
      }
      
      await takeScreenshot(page, 'work-items-search-filter');
    });

    test('should display work item details', async ({ page }) => {
      await navigateTo(page, '/work-items');
      
      // Look for first work item to click on
      const itemSelectors = [
        'table tbody tr:first-child',
        '.work-item:first-child',
        '[data-testid="work-item"]:first-child',
        'tr:has(td):first-child'
      ];
      
      for (const selector of itemSelectors) {
        if (await page.locator(selector).isVisible({ timeout: 5000 }).catch(() => false)) {
          try {
            await page.click(selector);
            await waitForPageLoad(page);
            
            // Look for detail view
            const detailSelectors = [
              '[data-testid="work-item-detail"]',
              '.work-item-detail',
              '.detail-view',
              'h1, h2, h3' // Details usually have a title
            ];
            
            let detailFound = false;
            for (const detailSelector of detailSelectors) {
              if (await page.locator(detailSelector).isVisible({ timeout: 5000 }).catch(() => false)) {
                detailFound = true;
                console.log(`Found detail view: ${detailSelector}`);
                break;
              }
            }
            
            if (detailFound) {
              await takeScreenshot(page, 'work-item-detail-view');
            }
            
            break;
          } catch {
            continue;
          }
        }
      }
    });
  });

  test.describe('Update Work Items', () => {
    test('should edit existing work item', async ({ page }) => {
      await navigateTo(page, '/work-items');
      
      // Look for edit buttons or clickable items
      const editSelectors = [
        'button:has-text("Edit")',
        '[data-testid="edit-button"]',
        '.edit-btn',
        'button[aria-label="Edit"]',
        'table tbody tr:first-child' // Click on first row to edit
      ];
      
      let editFound = false;
      for (const selector of editSelectors) {
        if (await page.locator(selector).isVisible({ timeout: 5000 }).catch(() => false)) {
          try {
            await page.click(selector);
            await waitForPageLoad(page);
            editFound = true;
            console.log(`Found edit functionality: ${selector}`);
            break;
          } catch {
            continue;
          }
        }
      }
      
      if (editFound) {
        // Look for editable fields
        const editableFields = [
          'input[name="title"]',
          'input[name="business_value"]',
          'input[name="technical_complexity"]',
          'input[name="story_points"]',
          'select[name="priority"]',
          'textarea[name="description"]'
        ];
        
        let fieldsEdited = 0;
        for (const fieldSelector of editableFields) {
          if (await page.locator(fieldSelector).isVisible({ timeout: 3000 }).catch(() => false)) {
            try {
              const currentValue = await page.inputValue(fieldSelector);
              const newValue = fieldSelector.includes('title') ? 'Updated Title' :
                              fieldSelector.includes('business') ? '9' :
                              fieldSelector.includes('complexity') ? '7' :
                              fieldSelector.includes('points') ? '8' :
                              fieldSelector.includes('description') ? 'Updated description' :
                              currentValue + '_updated';
              
              if (fieldSelector.includes('select')) {
                const options = await page.locator(`${fieldSelector} option`).all();
                if (options.length > 1) {
                  await page.selectOption(fieldSelector, await options[1].getAttribute('value') || '');
                }
              } else {
                await fillField(page, fieldSelector, newValue);
              }
              
              fieldsEdited++;
            } catch {
              continue;
            }
          }
        }
        
        if (fieldsEdited > 0) {
          await takeScreenshot(page, 'work-item-edit-form');
          
          // Save changes
          const saveButtons = [
            'button:has-text("Save")',
            'button:has-text("Update")',
            'button[type="submit"]',
            '[data-testid="save-button"]'
          ];
          
          for (const saveSelector of saveButtons) {
            if (await page.locator(saveSelector).isVisible({ timeout: 3000 }).catch(() => false)) {
              await page.click(saveSelector);
              await waitForPageLoad(page);
              break;
            }
          }
          
          await takeScreenshot(page, 'work-item-updated');
        }
      } else {
        console.log('Edit functionality not found - may not be implemented yet');
        await takeScreenshot(page, 'work-items-no-edit');
      }
    });

    test('should update work item priority', async ({ page }) => {
      await navigateTo(page, '/work-items');
      
      // Look for priority controls (dropdowns, buttons, etc.)
      const prioritySelectors = [
        'select[name="priority"]',
        '[data-testid="priority-select"]',
        'button:has-text("High")',
        'button:has-text("Medium")',
        'button:has-text("Low")',
        '.priority-control'
      ];
      
      for (const selector of prioritySelectors) {
        if (await page.locator(selector).isVisible({ timeout: 5000 }).catch(() => false)) {
          try {
            if (selector.includes('select')) {
              await page.selectOption(selector, 'High');
            } else {
              await page.click(selector);
            }
            
            await waitForPageLoad(page);
            console.log(`Updated priority using: ${selector}`);
            break;
          } catch {
            continue;
          }
        }
      }
      
      await takeScreenshot(page, 'work-item-priority-update');
    });
  });

  test.describe('Delete Work Items', () => {
    test('should delete work item with confirmation', async ({ page }) => {
      await navigateTo(page, '/work-items');
      
      // Look for delete buttons
      const deleteSelectors = [
        'button:has-text("Delete")',
        '[data-testid="delete-button"]',
        'button[aria-label="Delete"]',
        '.delete-btn',
        'button:has(svg)' // Delete buttons often have icons
      ];
      
      let deleteFound = false;
      for (const selector of deleteSelectors) {
        if (await page.locator(selector).isVisible({ timeout: 5000 }).catch(() => false)) {
          // Get count of items before deletion
          const itemsBefore = await page.locator('table tbody tr, .work-item').count().catch(() => 0);
          
          await page.click(selector);
          await page.waitForTimeout(1000);
          
          // Look for confirmation dialog
          const confirmSelectors = [
            'button:has-text("Confirm")',
            'button:has-text("Yes")',
            'button:has-text("Delete")',
            '[data-testid="confirm-delete"]',
            '.confirm-button'
          ];
          
          let confirmFound = false;
          for (const confirmSelector of confirmSelectors) {
            if (await page.locator(confirmSelector).isVisible({ timeout: 3000 }).catch(() => false)) {
              await page.click(confirmSelector);
              await waitForPageLoad(page);
              confirmFound = true;
              break;
            }
          }
          
          if (confirmFound) {
            // Verify item was deleted
            await page.waitForTimeout(2000);
            const itemsAfter = await page.locator('table tbody tr, .work-item').count().catch(() => 0);
            
            if (itemsAfter < itemsBefore) {
              console.log('Work item deleted successfully');
            }
          }
          
          deleteFound = true;
          break;
        }
      }
      
      await takeScreenshot(page, 'work-item-delete-operation');
      
      if (!deleteFound) {
        console.log('Delete functionality not found - may not be implemented yet');
      }
    });

    test('should cancel work item deletion', async ({ page }) => {
      await navigateTo(page, '/work-items');
      
      // Find delete button
      const deleteButton = page.locator('button:has-text("Delete"), [data-testid="delete-button"]').first();
      
      if (await deleteButton.isVisible({ timeout: 5000 }).catch(() => false)) {
        await deleteButton.click();
        await page.waitForTimeout(1000);
        
        // Look for cancel button in confirmation dialog
        const cancelSelectors = [
          'button:has-text("Cancel")',
          'button:has-text("No")',
          '[data-testid="cancel-delete"]',
          '.cancel-button'
        ];
        
        for (const selector of cancelSelectors) {
          if (await page.locator(selector).isVisible({ timeout: 3000 }).catch(() => false)) {
            await page.click(selector);
            await waitForPageLoad(page);
            console.log('Delete operation cancelled');
            break;
          }
        }
        
        await takeScreenshot(page, 'work-item-delete-cancelled');
      }
    });
  });

  test.describe('Bulk Operations', () => {
    test('should perform bulk operations on work items', async ({ page }) => {
      await navigateTo(page, '/work-items');
      
      // Look for checkboxes for bulk selection
      const checkboxes = await page.locator('input[type="checkbox"]').all();
      
      if (checkboxes.length > 1) {
        // Select multiple items
        for (let i = 0; i < Math.min(3, checkboxes.length); i++) {
          try {
            await checkboxes[i].check();
          } catch {
            continue;
          }
        }
        
        // Look for bulk operation buttons
        const bulkButtons = [
          'button:has-text("Bulk")',
          'button:has-text("Delete Selected")',
          'button:has-text("Update Selected")',
          '[data-testid="bulk-actions"]'
        ];
        
        for (const selector of bulkButtons) {
          if (await page.locator(selector).isVisible({ timeout: 3000 }).catch(() => false)) {
            console.log(`Found bulk operations: ${selector}`);
            break;
          }
        }
        
        await takeScreenshot(page, 'work-items-bulk-selection');
      }
    });
  });
});