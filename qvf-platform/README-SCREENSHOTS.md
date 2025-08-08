# QVF Platform Screenshot Automation

This directory contains automated screenshot capture for the QVF Platform using Playwright.

## Prerequisites

1. **QVF Platform Running**: The application must be running at:
   - Frontend: http://localhost:3006
   - Backend: http://localhost:8000

2. **Dependencies Installed**: 
   ```bash
   pnpm install
   ```

3. **Playwright Browsers**: Install Playwright browsers if not already done:
   ```bash
   npx playwright install
   ```

## Available Test Users

The automation uses these test users:

| Role | Username | Password |
|------|----------|----------|
| Executive | `executive` | `executive123` |
| Product Owner | `product_owner` | `po123` |
| Scrum Master | `scrum_master` | `sm123` |

## Running Screenshot Automation

### Option 1: Using Playwright Test Suite
```bash
# Run the full Playwright test suite
pnpm run test:e2e

# Run only screenshot tests
pnpm run screenshots

# Run with UI mode (interactive)
pnpm run test:e2e:ui
```

### Option 2: Using the Standalone Script
```bash
# Install node-fetch if not already installed
npm install node-fetch

# Run the standalone script
node capture-screenshots.js
```

## Screenshots Captured

The automation will capture the following screenshots:

### Desktop Screenshots (1440x900)
1. **qvf-01-login-page.png** - Login page
2. **qvf-02-executive-dashboard.png** - Executive user dashboard
3. **qvf-03-executive-full-view.png** - Additional executive views (if available)
4. **qvf-04-product-owner-dashboard.png** - Product Owner dashboard
5. **qvf-05-work-items-page.png** - Work Items page (if available)
6. **qvf-06-qvf-comparison-page.png** - QVF Comparison page (if available)
7. **qvf-09-final-state.png** - Final application state

### Mobile Screenshots (375x812)
8. **qvf-07-mobile-login.png** - Mobile login view
9. **qvf-08-mobile-dashboard.png** - Mobile dashboard view

## Automation Features

### Robust Element Detection
The automation uses multiple selector strategies to find UI elements:
- Data test IDs (`data-testid`)
- Standard HTML attributes (`name`, `type`)
- Text content matching (`:has-text()`)
- Fallback navigation methods

### Error Handling
- Graceful fallbacks when pages aren't found
- Multiple retry strategies for element interaction
- Network idle waiting for proper page loads
- Timeout handling for slow-loading elements

### User Flow Simulation
1. **Login Flow**: Tests login functionality with different users
2. **Navigation**: Attempts to navigate to key application pages
3. **Logout/Switch**: Tests user switching functionality
4. **Responsive Testing**: Captures both desktop and mobile views

## Configuration

### Playwright Configuration
The `playwright.config.ts` file includes:
- Base URL configuration (`http://localhost:3006`)
- Multiple browser support (Chromium, Firefox, WebKit)
- Trace collection for debugging
- HTML reporter for test results

### Viewport Sizes
- **Desktop**: 1440x900 (standard laptop resolution)
- **Mobile**: 375x812 (iPhone X dimensions)

## Troubleshooting

### Application Not Running
```
❌ QVF Platform is not accessible at http://localhost:3006
```
**Solution**: Start the application:
```bash
pnpm run dev
```

### Login Issues
If login automation fails:
1. Check if test users are properly configured in the backend
2. Verify the login form element selectors
3. Check browser console for JavaScript errors

### Page Not Found
If specific pages (Work Items, QVF Comparison) aren't found:
1. Verify the routes exist in the application
2. Check navigation menu structure
3. Update selectors in the test files

### Screenshot Quality
For better screenshot quality:
- Ensure application is fully loaded before capture
- Check for loading animations or async content
- Adjust wait times in the automation scripts

## Customization

### Adding New Screenshots
To capture additional pages:

1. **In Playwright test** (`tests/qvf-screenshots.spec.ts`):
   ```typescript
   // Navigate to new page
   await page.goto('/new-page');
   await waitForPageLoad(page);
   
   // Capture screenshot
   await page.screenshot({
     path: 'qvf-new-page.png',
     fullPage: true,
   });
   ```

2. **In standalone script** (`capture-screenshots.js`):
   ```javascript
   // Add navigation logic
   await page.goto('http://localhost:3006/new-page');
   await waitForPageLoad(page);
   
   // Capture screenshot
   await page.screenshot({
     path: path.join(__dirname, 'qvf-new-page.png'),
     fullPage: true,
   });
   ```

### Modifying Selectors
Update element selectors in the respective files:
- Login selectors: `usernameSelectors`, `passwordSelectors`, `loginButtonSelectors`
- Navigation selectors: `workItemsSelectors`, `qvfComparisonSelectors`
- Logout selectors: `logoutSelectors`

## Output

All screenshots are saved in the `/Users/umasankrudhya/Projects/ds-package/qvf-platform/` directory with descriptive filenames and timestamps in the console output.

The automation provides detailed console feedback showing:
- ✅ Successful captures
- ⚠️ Warnings for optional content not found  
- ❌ Errors for critical failures
- ℹ️ Informational messages about the process