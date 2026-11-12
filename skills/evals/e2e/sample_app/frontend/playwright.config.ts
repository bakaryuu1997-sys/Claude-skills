import { defineConfig, devices } from '@playwright/test';

// E2E runs against a live backend (NEXT_PUBLIC_API_MODE=live). Required: BACKEND_URL reachable and seeded test accounts.
export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: false,
  retries: 0,
  expect: { timeout: 15_000 },
  reporter: [['list'], ['json', { outputFile: 'test-results/e2e-results.json' }]],
  use: { baseURL: process.env.E2E_BASE_URL ?? 'http://localhost:3001', trace: 'retain-on-failure' },
  // E2E_CHANNEL=msedge uses the installed Edge (no browser download); default is the bundled Chromium.
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'], channel: process.env.E2E_CHANNEL || undefined } }],
  webServer: {
    command: 'npm run build && npm run start',
    url: 'http://localhost:3001/login',
    reuseExistingServer: true,
    timeout: 180_000,
  },
});
