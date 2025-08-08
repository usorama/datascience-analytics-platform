import { test as cleanup } from '@playwright/test';
import { promises as fs } from 'fs';
import path from 'path';

/**
 * Authentication cleanup for QVF Platform E2E tests
 * Removes stored authentication states after tests complete
 */

cleanup('cleanup auth states', async ({}) => {
  const authDir = path.join('test-results', 'auth');
  
  try {
    // Remove all authentication state files
    await fs.rm(authDir, { recursive: true, force: true });
    console.log('✅ Authentication states cleaned up');
  } catch (error) {
    console.log('ℹ️  No authentication states to clean up');
  }
});