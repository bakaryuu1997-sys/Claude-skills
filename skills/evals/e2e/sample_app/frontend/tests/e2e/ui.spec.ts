import { expect, test } from '@playwright/test';
import { login } from './helpers';

test.describe('UI shell', () => {
  test('[UI-E2E-001] NEW Ctrl+K opens the command palette and navigates', async ({ page }) => {
    await login(page, 'employee');
    await page.keyboard.press('Control+K');
    await expect(page.getByRole('dialog', { name: 'コマンドパレット' })).toBeVisible();
    await page.getByRole('dialog', { name: 'コマンドパレット' }).getByRole('combobox').fill('新規');
    await page.keyboard.press('Enter');
    await expect(page).toHaveURL(/\/requests\/new$/);
  });

  test('[UI-E2E-002] NEW switching to the dark theme applies one theme to header and content', async ({ page }) => {
    await login(page, 'employee');
    await page.getByLabel('テーマ').selectOption('dark');
    await expect(page.locator('html')).toHaveClass(/dark/);
    const bodyBg = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
    const headerBg = await page.evaluate(() => getComputedStyle(document.querySelector('header')!).backgroundColor);
    // both surfaces are dark: every RGB channel below 100
    for (const colour of [bodyBg, headerBg]) {
      const channels = colour.match(/\d+/g)!.slice(0, 3).map(Number);
      expect(Math.max(...channels)).toBeLessThan(100);
    }
  });
});
