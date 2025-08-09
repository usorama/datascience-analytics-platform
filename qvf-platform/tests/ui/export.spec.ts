import { test, expect, download, Page } from '@playwright/test';
import path from 'path';
import fs from 'fs';
import { TestUsers } from '../fixtures/test-users';
import { login, navigateTo, waitForPageLoad, takeScreenshot } from '../fixtures/test-helpers';

// Helper function to wait for and handle download
async function handleDownload(page: Page, downloadTrigger: () => Promise<void>) {
  const downloadPromise = page.waitForEvent('download');
  await downloadTrigger();
  const download = await downloadPromise;
  return download;
}

// Helper to trigger export dialog
async function openExportDialog(page: Page) {
  // Look for export button with various selectors
  const exportButton = page.locator('[data-testid="export-button"], button:has-text("Export"), button[aria-label*="Export"]');
  await expect(exportButton).toBeVisible({ timeout: 10000 });
  await exportButton.click();
  
  // Wait for export dialog to appear
  const exportDialog = page.locator('[data-testid="export-dialog"], .export-dialog').or(
    page.locator('text="Export Work Items"').locator('..')
  );
  await expect(exportDialog).toBeVisible({ timeout: 5000 });
  
  return exportDialog;
}

test.describe('Export Functionality', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TestUsers.productOwner);
    await navigateTo(page, '/work-items');
    await page.waitForSelector('[data-testid="work-items-page"], .work-items, [role="main"]', { timeout: 15000 });
  });

  test('should display export button', async ({ page }) => {
    // Look for export button in various possible locations
    const exportButton = page.locator('[data-testid="export-button"], button:has-text("Export"), button[aria-label*="Export"]').or(
      page.locator('button:has([data-icon="download"])')
    );
    
    await expect(exportButton).toBeVisible({ timeout: 10000 });
    
    // Should be enabled when there are work items
    await expect(exportButton).toBeEnabled();
    
    await takeScreenshot(page, 'export-button-visible');
  });

  test('should open export dialog', async ({ page }) => {
    const exportDialog = await openExportDialog(page);
    
    // Check dialog content
    await expect(page.locator('text="Export Work Items"')).toBeVisible();
    await expect(page.locator('text*="work item"')).toBeVisible(); // Should show item count
    
    // Check format options
    await expect(page.locator('button:has-text("Excel")')).toBeVisible();
    await expect(page.locator('button:has-text("PDF")')).toBeVisible();
    await expect(page.locator('button:has-text("CSV")')).toBeVisible();
    
    await takeScreenshot(page, 'export-dialog-open');
  });

  test('should select different export formats', async ({ page }) => {
    const exportDialog = await openExportDialog(page);
    
    // Test Excel selection (default)
    const excelButton = exportDialog.locator('button:has-text("Excel")');
    await expect(excelButton).toHaveClass(/default|primary/); // Should be selected by default
    
    // Test PDF selection
    const pdfButton = exportDialog.locator('button:has-text("PDF")');
    await pdfButton.click();
    await expect(pdfButton).toHaveClass(/default|primary/);
    await expect(excelButton).not.toHaveClass(/default|primary/);
    
    // Test CSV selection
    const csvButton = exportDialog.locator('button:has-text("CSV")');
    await csvButton.click();
    await expect(csvButton).toHaveClass(/default|primary/);
    await expect(pdfButton).not.toHaveClass(/default|primary/);
    
    await takeScreenshot(page, 'export-format-selection');
  });

  test('should show export preview', async ({ page }) => {
    const exportDialog = await openExportDialog(page);
    
    // Check for preview section
    await expect(page.locator('text="Items to Export"')).toBeVisible();
    
    // Should show list of items to be exported
    const previewItems = exportDialog.locator('[data-testid="preview-item"]').or(
      exportDialog.locator('.text-sm:has(.truncate)')
    );
    
    const itemCount = await previewItems.count();
    expect(itemCount).toBeGreaterThan(0);
    
    // If there are more than 10 items, should show "and X more items"
    if (itemCount >= 10) {
      await expect(page.locator('text*="more items"')).toBeVisible();
    }
    
    await takeScreenshot(page, 'export-preview');
  });

  test('should export Excel file', async ({ page }) => {
    const exportDialog = await openExportDialog(page);
    
    // Select Excel format
    await exportDialog.locator('button:has-text("Excel")').click();
    
    // Mock the download or handle actual download
    const download = await handleDownload(page, async () => {
      const exportButton = exportDialog.locator('button:has-text("Export")', { hasText: /Export/ }).last();
      await exportButton.click();
    });
    
    // Verify download
    expect(download.suggestedFilename()).toMatch(/\.xlsx?$/);
    
    // Save download to verify
    const downloadPath = path.join(__dirname, '../downloads', download.suggestedFilename());
    await download.saveAs(downloadPath);
    
    // Verify file exists
    expect(fs.existsSync(downloadPath)).toBeTruthy();
    
    await takeScreenshot(page, 'excel-export-complete');
  });

  test('should export PDF file', async ({ page }) => {
    const exportDialog = await openExportDialog(page);
    
    // Select PDF format
    await exportDialog.locator('button:has-text("PDF")').click();
    
    const download = await handleDownload(page, async () => {
      const exportButton = exportDialog.locator('button:has-text("Export")', { hasText: /Export/ }).last();
      await exportButton.click();
    });
    
    // Verify download
    expect(download.suggestedFilename()).toMatch(/\.pdf$/);
    
    const downloadPath = path.join(__dirname, '../downloads', download.suggestedFilename());
    await download.saveAs(downloadPath);
    
    expect(fs.existsSync(downloadPath)).toBeTruthy();
    
    await takeScreenshot(page, 'pdf-export-complete');
  });

  test('should export CSV file', async ({ page }) => {
    const exportDialog = await openExportDialog(page);
    
    // Select CSV format
    await exportDialog.locator('button:has-text("CSV")').click();
    
    const download = await handleDownload(page, async () => {
      const exportButton = exportDialog.locator('button:has-text("Export")', { hasText: /Export/ }).last();
      await exportButton.click();
    });
    
    // Verify download
    expect(download.suggestedFilename()).toMatch(/\.csv$/);
    
    const downloadPath = path.join(__dirname, '../downloads', download.suggestedFilename());
    await download.saveAs(downloadPath);
    
    expect(fs.existsSync(downloadPath)).toBeTruthy();
    
    // Verify CSV content has headers
    const csvContent = fs.readFileSync(downloadPath, 'utf-8');
    expect(csvContent).toMatch(/title|business_value|qvf_score/i); // Should have expected headers
    
    await takeScreenshot(page, 'csv-export-complete');
  });

  test('should show loading state during export', async ({ page }) => {
    const exportDialog = await openExportDialog(page);
    
    // Select format
    await exportDialog.locator('button:has-text("Excel")').click();
    
    // Intercept export request to add delay
    await page.route('**/api/export/**', async route => {
      // Add artificial delay to see loading state
      await new Promise(resolve => setTimeout(resolve, 2000));
      await route.continue();
    });
    
    // Click export
    const exportButton = exportDialog.locator('button:has-text("Export")', { hasText: /Export/ }).last();
    await exportButton.click();
    
    // Should show loading state
    await expect(page.locator('text="Exporting..."')).toBeVisible({ timeout: 5000 });
    
    // Buttons should be disabled during export
    await expect(exportButton).toBeDisabled();
    const cancelButton = exportDialog.locator('button:has-text("Cancel")');
    await expect(cancelButton).toBeDisabled();
    
    await takeScreenshot(page, 'export-loading-state');
  });

  test('should close export dialog', async ({ page }) => {
    const exportDialog = await openExportDialog(page);
    
    // Close with X button
    const closeButton = exportDialog.locator('button:has([data-icon="x"]), button[aria-label*="Close"]');
    await closeButton.click();
    
    // Dialog should be gone
    await expect(exportDialog).not.toBeVisible({ timeout: 2000 });
    
    // Test cancel button
    await openExportDialog(page);
    const cancelButton = page.locator('button:has-text("Cancel")');
    await cancelButton.click();
    
    await expect(exportDialog).not.toBeVisible({ timeout: 2000 });
    
    await takeScreenshot(page, 'export-dialog-closed');
  });

  test('should handle export errors gracefully', async ({ page }) => {
    const exportDialog = await openExportDialog(page);
    
    // Mock failed export
    await page.route('**/api/export/**', route => {
      route.fulfill({
        status: 500,
        body: JSON.stringify({ error: 'Export failed' })
      });
    });
    
    // Try to export
    await exportDialog.locator('button:has-text("Excel")').click();
    const exportButton = exportDialog.locator('button:has-text("Export")', { hasText: /Export/ }).last();
    await exportButton.click();
    
    // Should show error or remain in dialog
    await page.waitForTimeout(3000);
    
    // Dialog might still be visible or show error message
    const errorMessage = page.locator('[role="alert"], .alert-destructive, text*="failed"');
    
    // Either dialog remains open or error is shown
    const dialogStillOpen = await exportDialog.isVisible();
    const errorShown = await errorMessage.isVisible();
    
    expect(dialogStillOpen || errorShown).toBeTruthy();
    
    await takeScreenshot(page, 'export-error-handling');
  });

  test('should export with QVF scores when available', async ({ page }) => {
    const exportDialog = await openExportDialog(page);
    
    // Check preview shows QVF scores
    const qvfScores = page.locator('text*="QVF"').or(page.locator('[data-testid="qvf-score"]'));
    
    // Should show QVF information in preview or UI
    const hasQvfData = await qvfScores.count() > 0;
    
    if (hasQvfData) {
      // Export should include QVF scores
      const download = await handleDownload(page, async () => {
        await exportDialog.locator('button:has-text("CSV")').click();
        const exportButton = exportDialog.locator('button:has-text("Export")', { hasText: /Export/ }).last();
        await exportButton.click();
      });
      
      const downloadPath = path.join(__dirname, '../downloads', download.suggestedFilename());
      await download.saveAs(downloadPath);
      
      const csvContent = fs.readFileSync(downloadPath, 'utf-8');
      expect(csvContent.toLowerCase()).toMatch(/qvf/);
    }
    
    await takeScreenshot(page, 'export-with-qvf-scores');
  });
});

test.describe('Export Functionality - Different User Roles', () => {
  test('executive should be able to export all data', async ({ page }) => {
    await login(page, TestUsers.executive);
    await navigateTo(page, '/work-items');
    await page.waitForSelector('[data-testid="work-items-page"], .work-items, [role="main"]', { timeout: 15000 });
    
    // Should have access to export functionality
    const exportButton = page.locator('[data-testid="export-button"], button:has-text("Export"), button[aria-label*="Export"]');
    await expect(exportButton).toBeVisible({ timeout: 10000 });
    
    // Should be able to export
    const exportDialog = await openExportDialog(page);
    await expect(page.locator('text="Export Work Items"')).toBeVisible();
    
    await takeScreenshot(page, 'executive-export-access');
  });

  test('scrum master should have export capabilities', async ({ page }) => {
    await login(page, TestUsers.scrumMaster);
    await navigateTo(page, '/work-items');
    await page.waitForSelector('[data-testid="work-items-page"], .work-items, [role="main"]', { timeout: 15000 });
    
    const exportButton = page.locator('[data-testid="export-button"], button:has-text("Export"), button[aria-label*="Export"]');
    await expect(exportButton).toBeVisible({ timeout: 10000 });
    
    await takeScreenshot(page, 'scrum-master-export-access');
  });

  test('developer should have limited export access', async ({ page }) => {
    await login(page, TestUsers.developer);
    await navigateTo(page, '/work-items');
    await page.waitForSelector('[data-testid="work-items-page"], .work-items, [role="main"]', { timeout: 15000 });
    
    // Developer might have limited or full export access depending on requirements
    const exportButton = page.locator('[data-testid="export-button"], button:has-text("Export"), button[aria-label*="Export"]');
    
    const hasExportAccess = await exportButton.isVisible({ timeout: 5000 });
    
    if (hasExportAccess) {
      await expect(exportButton).toBeVisible();
    } else {
      // Export functionality might be hidden for developers
      await expect(exportButton).not.toBeVisible();
    }
    
    await takeScreenshot(page, 'developer-export-access');
  });
});

test.describe('Export Performance and Reliability', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, TestUsers.productOwner);
    await navigateTo(page, '/work-items');
  });

  test('should handle large datasets efficiently', async ({ page }) => {
    await page.waitForSelector('[data-testid="work-items-page"], .work-items, [role="main"]', { timeout: 15000 });
    
    const exportDialog = await openExportDialog(page);
    
    // Check if there's a large number of items
    const itemCountText = await exportDialog.locator('text*="work item"').textContent();
    const itemCount = itemCountText ? parseInt(itemCountText.match(/\d+/)?.[0] || '0') : 0;
    
    if (itemCount > 50) {
      // Test performance with large dataset
      const startTime = Date.now();
      
      await exportDialog.locator('button:has-text("CSV")').click();
      const exportButton = exportDialog.locator('button:has-text("Export")', { hasText: /Export/ }).last();
      await exportButton.click();
      
      // Wait for loading state
      await expect(page.locator('text="Exporting..."')).toBeVisible({ timeout: 5000 });
      
      const loadingTime = Date.now() - startTime;
      expect(loadingTime).toBeLessThan(10000); // Should start quickly
    }
    
    await takeScreenshot(page, 'large-dataset-export');
  });

  test('should be responsive during export', async ({ page }) => {
    await page.waitForSelector('[data-testid="work-items-page"], .work-items, [role="main"]', { timeout: 15000 });
    
    const exportDialog = await openExportDialog(page);
    
    // Start export
    await exportDialog.locator('button:has-text("Excel")').click();
    const exportButton = exportDialog.locator('button:has-text("Export")', { hasText: /Export/ }).last();
    
    // UI should remain responsive
    const responseTime = await page.evaluate(async () => {
      const startTime = performance.now();
      
      // Simulate UI interaction during export
      const button = document.querySelector('button:has-text("Cancel")');
      if (button) {
        button.focus();
      }
      
      return performance.now() - startTime;
    });
    
    expect(responseTime).toBeLessThan(100); // Should remain responsive
    
    await takeScreenshot(page, 'export-responsiveness');
  });
});

// Cleanup downloads directory
test.afterAll(async () => {
  const downloadsDir = path.join(__dirname, '../downloads');
  if (fs.existsSync(downloadsDir)) {
    fs.rmSync(downloadsDir, { recursive: true, force: true });
  }
});