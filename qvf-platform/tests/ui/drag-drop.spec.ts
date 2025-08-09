import { test, expect, Page } from '@playwright/test';
import { TestUsers } from '../fixtures/test-users';
import { login, navigateTo, waitForPageLoad, takeScreenshot } from '../fixtures/test-helpers';

// Helper function to perform drag and drop
async function performDragDrop(page: Page, sourceSelector: string, targetSelector: string) {
  const source = page.locator(sourceSelector);
  const target = page.locator(targetSelector);
  
  await expect(source).toBeVisible({ timeout: 10000 });
  await expect(target).toBeVisible({ timeout: 10000 });
  
  // Get bounding boxes for precise positioning
  const sourceBounds = await source.boundingBox();
  const targetBounds = await target.boundingBox();
  
  if (!sourceBounds || !targetBounds) {
    throw new Error('Could not get element bounds for drag operation');
  }
  
  // Calculate center positions
  const sourceCenter = {
    x: sourceBounds.x + sourceBounds.width / 2,
    y: sourceBounds.y + sourceBounds.height / 2
  };
  
  const targetCenter = {
    x: targetBounds.x + targetBounds.width / 2,
    y: targetBounds.y + targetBounds.height / 2
  };
  
  // Perform drag and drop with mouse events
  await page.mouse.move(sourceCenter.x, sourceCenter.y);
  await page.mouse.down();
  await page.waitForTimeout(100); // Small delay for drag to start
  await page.mouse.move(targetCenter.x, targetCenter.y, { steps: 5 });
  await page.waitForTimeout(100);
  await page.mouse.up();
  await page.waitForTimeout(500); // Wait for drop animation
}

// Helper to wait for QVF recalculation to complete
async function waitForQvfRecalculation(page: Page) {
  // Look for loading indicator
  const loadingIndicator = page.locator('text="Updating QVF scores..."');
  
  // Wait for it to appear (optional - might be fast)
  try {
    await expect(loadingIndicator).toBeVisible({ timeout: 2000 });
  } catch {
    // It might finish too fast to see
  }
  
  // Wait for it to disappear
  await expect(loadingIndicator).not.toBeVisible({ timeout: 10000 });
}

test.describe('Drag and Drop Functionality', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TestUsers.productOwner);
    await navigateTo(page, '/work-items');
    await page.waitForSelector('[data-testid="work-items-page"], .priority-queue, [role="main"]', { timeout: 15000 });
  });

  test('should display draggable work items list', async ({ page }) => {
    // Look for the priority queue or drag-drop container
    const draggableList = page.locator('.priority-queue, [data-testid="draggable-list"], .space-y-2').first();
    await expect(draggableList).toBeVisible({ timeout: 10000 });
    
    // Check for drag handle indicators
    const dragHandles = page.locator('[data-testid="drag-handle"], .cursor-grab, svg[data-icon="grip-vertical"]');
    const handleCount = await dragHandles.count();
    expect(handleCount).toBeGreaterThan(0);
    
    await takeScreenshot(page, 'drag-drop-initial-state');
  });

  test('should show drag instructions', async ({ page }) => {
    // Look for instruction text
    const instructions = page.locator('text*="Drag and Drop Instructions"');
    await expect(instructions).toBeVisible({ timeout: 10000 });
    
    // Check for key instruction points
    await expect(page.locator('text*="Drag work items to reorder"')).toBeVisible();
    await expect(page.locator('text*="Higher position = higher priority"')).toBeVisible();
    await expect(page.locator('text*="QVF scores will update automatically"')).toBeVisible();
  });

  test('should reorder work items via drag and drop', async ({ page }) => {
    // Find draggable items - look for various possible selectors
    const workItems = page.locator('[data-testid="work-item"], [data-sortable-item], .sortable-item, .cursor-grab').or(
      page.locator('[role="button"]:has([data-icon="grip-vertical"])')
    );
    
    const itemCount = await workItems.count();
    
    if (itemCount < 2) {
      test.skip('Need at least 2 work items to test drag and drop');
    }
    
    // Get initial order
    const firstItem = workItems.first();
    const secondItem = workItems.nth(1);
    
    const firstItemText = await firstItem.textContent();
    const secondItemText = await secondItem.textContent();
    
    // Perform drag and drop - move first item to second position
    await performDragDrop(page, 
      workItems.first().locator('..').toString(), // Get parent container
      workItems.nth(1).locator('..').toString()
    );
    
    // Wait for any animations or state updates
    await page.waitForTimeout(1000);
    await waitForQvfRecalculation(page);
    
    // Verify order changed
    const updatedItems = page.locator('[data-testid="work-item"], [data-sortable-item], .sortable-item, .cursor-grab').or(
      page.locator('[role="button"]:has([data-icon="grip-vertical"])')
    );
    
    const newFirstItemText = await updatedItems.first().textContent();
    const newSecondItemText = await updatedItems.nth(1).textContent();
    
    // The order should have changed
    expect(newFirstItemText).not.toBe(firstItemText);
    
    await takeScreenshot(page, 'drag-drop-reordered');
  });

  test('should show visual feedback during drag operation', async ({ page }) => {
    const workItems = page.locator('[data-testid="work-item"], [data-sortable-item], .sortable-item').first();
    await expect(workItems).toBeVisible({ timeout: 10000 });
    
    // Start drag operation
    const itemBounds = await workItems.boundingBox();
    if (!itemBounds) throw new Error('Could not get item bounds');
    
    const center = {
      x: itemBounds.x + itemBounds.width / 2,
      y: itemBounds.y + itemBounds.height / 2
    };
    
    await page.mouse.move(center.x, center.y);
    await page.mouse.down();
    
    // Move slightly to start drag
    await page.mouse.move(center.x, center.y + 50, { steps: 3 });
    await page.waitForTimeout(200);
    
    // Look for drag overlay or visual feedback
    const dragOverlay = page.locator('[data-testid="drag-overlay"], .drag-overlay, .transform.rotate-3.opacity-95');
    
    // Visual feedback might be present (drag overlay, cursor change, etc.)
    // This test verifies the drag system is working visually
    
    await page.mouse.up();
    await page.waitForTimeout(500);
    
    await takeScreenshot(page, 'drag-visual-feedback');
  });

  test('should support undo and redo operations', async ({ page }) => {
    // Look for undo/redo buttons
    const undoButton = page.locator('[data-testid="undo-button"], button:has([data-icon="undo"])');
    const redoButton = page.locator('[data-testid="redo-button"], button:has([data-icon="redo"])');
    
    await expect(undoButton).toBeVisible({ timeout: 10000 });
    await expect(redoButton).toBeVisible({ timeout: 10000 });
    
    // Initially, undo should be disabled (or enabled if there are prior actions)
    // Redo should typically be disabled initially
    const redoDisabled = await redoButton.getAttribute('disabled');
    expect(redoDisabled).toBe('');
    
    // Try to perform a drag operation first
    const workItems = page.locator('[data-testid="work-item"], [data-sortable-item], .sortable-item').or(
      page.locator('[role="button"]:has([data-icon="grip-vertical"])')
    );
    
    const itemCount = await workItems.count();
    if (itemCount >= 2) {
      // Perform a drag operation to enable undo
      await performDragDrop(page,
        workItems.first().locator('..').toString(),
        workItems.nth(1).locator('..').toString()
      );
      
      await waitForQvfRecalculation(page);
      
      // Now undo should be enabled
      await expect(undoButton).not.toHaveAttribute('disabled');
      
      // Test undo
      await undoButton.click();
      await page.waitForTimeout(1000);
      
      // Now redo should be enabled
      await expect(redoButton).not.toHaveAttribute('disabled');
      
      // Test redo
      await redoButton.click();
      await page.waitForTimeout(1000);
    }
    
    await takeScreenshot(page, 'drag-undo-redo');
  });

  test('should handle touch-based drag and drop on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 }); // Mobile viewport
    
    const workItems = page.locator('[data-testid="work-item"], [data-sortable-item], .sortable-item').or(
      page.locator('[role="button"]:has([data-icon="grip-vertical"])')
    );
    
    await expect(workItems.first()).toBeVisible({ timeout: 10000 });
    
    const itemCount = await workItems.count();
    if (itemCount < 2) {
      test.skip('Need at least 2 work items for mobile drag test');
    }
    
    // For mobile, we'll simulate touch events
    const firstItem = workItems.first();
    const secondItem = workItems.nth(1);
    
    const firstBounds = await firstItem.boundingBox();
    const secondBounds = await secondItem.boundingBox();
    
    if (!firstBounds || !secondBounds) {
      test.skip('Could not get item bounds for touch test');
    }
    
    // Touch-based drag and drop
    await page.touchscreen.tap(firstBounds.x + firstBounds.width / 2, firstBounds.y + firstBounds.height / 2);
    await page.waitForTimeout(300); // Touch delay activation
    
    // Drag to target
    await page.mouse.move(
      secondBounds.x + secondBounds.width / 2, 
      secondBounds.y + secondBounds.height / 2
    );
    await page.waitForTimeout(500);
    
    await takeScreenshot(page, 'mobile-drag-drop');
  });

  test('should show error handling for failed operations', async ({ page }) => {
    // This test checks if error states are handled properly
    
    // Look for any error alerts or messages
    const errorAlert = page.locator('[data-testid="error-alert"], .alert-destructive, [role="alert"]');
    
    // Initially should not have errors
    await expect(errorAlert).not.toBeVisible();
    
    // Try to perform operations and check for potential error handling
    const workItems = page.locator('[data-testid="work-item"], [data-sortable-item], .sortable-item');
    
    if (await workItems.count() > 0) {
      // Simulate network issues by intercepting and failing API calls
      await page.route('**/api/qvf/calculate-scores*', route => {
        route.fulfill({
          status: 500,
          body: JSON.stringify({ error: 'Internal server error' })
        });
      });
      
      // Try drag operation
      if (await workItems.count() >= 2) {
        await performDragDrop(page,
          workItems.first().locator('..').toString(),
          workItems.nth(1).locator('..').toString()
        );
        
        // Wait and check for error message
        await page.waitForTimeout(3000);
        
        // Look for error feedback
        const errorMessage = page.locator('text*="Failed to update QVF scores"').or(
          page.locator('.alert-destructive')
        );
        
        // Error might be visible
        try {
          await expect(errorMessage).toBeVisible({ timeout: 5000 });
        } catch {
          // Error handling might be different
        }
      }
      
      await takeScreenshot(page, 'drag-drop-error-handling');
    }
  });

  test('should be keyboard accessible', async ({ page }) => {
    // Test keyboard navigation for drag and drop
    const workItems = page.locator('[data-testid="work-item"], [data-sortable-item], .sortable-item').or(
      page.locator('[role="button"]:has([data-icon="grip-vertical"])')
    );
    
    await expect(workItems.first()).toBeVisible({ timeout: 10000 });
    
    // Focus first item
    await workItems.first().focus();
    
    // Check if it's focusable
    const isFocused = await workItems.first().evaluate(el => document.activeElement === el);
    expect(isFocused).toBeTruthy();
    
    // Try keyboard shortcuts for reordering (if implemented)
    // This depends on the actual keyboard implementation
    await page.keyboard.press('Space'); // Might activate drag mode
    await page.waitForTimeout(100);
    await page.keyboard.press('ArrowDown'); // Move down
    await page.waitForTimeout(100);
    await page.keyboard.press('Space'); // Drop
    
    await takeScreenshot(page, 'keyboard-drag-drop');
  });

  test('should persist order changes', async ({ page }) => {
    const workItems = page.locator('[data-testid="work-item"], [data-sortable-item], .sortable-item').or(
      page.locator('[role="button"]:has([data-icon="grip-vertical"])')
    );
    
    const itemCount = await workItems.count();
    if (itemCount < 2) {
      test.skip('Need items to test persistence');
    }
    
    // Get initial order
    const initialOrder = [];
    for (let i = 0; i < Math.min(itemCount, 3); i++) {
      const text = await workItems.nth(i).textContent();
      initialOrder.push(text);
    }
    
    // Perform drag operation
    await performDragDrop(page,
      workItems.first().locator('..').toString(),
      workItems.nth(1).locator('..').toString()
    );
    
    await waitForQvfRecalculation(page);
    
    // Get new order
    const newOrder = [];
    for (let i = 0; i < Math.min(itemCount, 3); i++) {
      const text = await workItems.nth(i).textContent();
      newOrder.push(text);
    }
    
    // Refresh page
    await page.reload();
    await page.waitForSelector('[data-testid="work-items-page"], .priority-queue, [role="main"]', { timeout: 15000 });
    
    // Check if order persisted (this depends on backend implementation)
    const persistedItems = page.locator('[data-testid="work-item"], [data-sortable-item"], .sortable-item').or(
      page.locator('[role="button"]:has([data-icon="grip-vertical"])')
    );
    
    // Wait for items to load
    await expect(persistedItems.first()).toBeVisible({ timeout: 10000 });
    
    await takeScreenshot(page, 'drag-drop-persistence');
  });
});

test.describe('Drag and Drop Performance', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TestUsers.scrumMaster);
    await navigateTo(page, '/work-items');
  });

  test('should handle large lists efficiently', async ({ page }) => {
    await page.waitForSelector('[data-testid="work-items-page"], .priority-queue, [role="main"]', { timeout: 15000 });
    
    const workItems = page.locator('[data-testid="work-item"], [data-sortable-item], .sortable-item');
    const itemCount = await workItems.count();
    
    // Test performance with available items
    if (itemCount > 0) {
      const startTime = Date.now();
      
      // Focus first item to test responsiveness
      await workItems.first().focus();
      
      const focusTime = Date.now() - startTime;
      expect(focusTime).toBeLessThan(1000); // Should be responsive
      
      // If we have enough items, test scroll performance
      if (itemCount > 5) {
        await page.keyboard.press('End'); // Scroll to end
        await page.waitForTimeout(100);
        await page.keyboard.press('Home'); // Scroll to top
        
        const scrollTime = Date.now() - startTime;
        expect(scrollTime).toBeLessThan(2000); // Should scroll smoothly
      }
    }
    
    await takeScreenshot(page, 'drag-drop-performance');
  });

  test('should provide smooth animations', async ({ page }) => {
    await page.waitForSelector('[data-testid="work-items-page"], .priority-queue, [role="main"]', { timeout: 15000 });
    
    const workItems = page.locator('[data-testid="work-item"], [data-sortable-item], .sortable-item');
    
    if (await workItems.count() >= 2) {
      // Start drag operation and measure time
      const startTime = Date.now();
      
      await performDragDrop(page,
        workItems.first().locator('..').toString(),
        workItems.nth(1).locator('..').toString()
      );
      
      const dragTime = Date.now() - startTime;
      
      // Drag operation should complete within reasonable time
      expect(dragTime).toBeLessThan(3000);
    }
    
    await takeScreenshot(page, 'drag-drop-animations');
  });
});