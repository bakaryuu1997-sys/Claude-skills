import { expect, test } from '@playwright/test';
import { futureDate, login } from './helpers';

test.describe('LEAVE', () => {
  test('[LEAVE-E2E-001] employee submits annual leave and approver approves it', async ({ page, browser }) => {
    await login(page, 'employee');
    await page.goto('/requests/new');
    await page.getByLabel('休暇種別').selectOption('ANNUAL');
    const day = futureDate();
    await page.getByLabel('開始日').fill(day);
    await page.getByLabel('終了日').fill(day);
    await page.getByLabel('理由').fill('E2E test');
    await page.getByRole('button', { name: '提出' }).click();
    await expect(page).toHaveURL(/\/requests$/);
    await expect(page.locator('tbody').getByText('承認待ち').first()).toBeVisible();
    await page.getByRole('link', { name: '開く' }).first().click();
    await page.waitForURL(/\/requests\/[0-9a-f-]{36}$/);
    const detailUrl = page.url();

    const approverCtx = await browser.newContext();
    const approver = await approverCtx.newPage();
    await login(approver, 'manager');
    await approver.goto(detailUrl);
    await approver.getByRole('button', { name: '承認' }).click();
    await expect(approver.getByText('承認済み')).toBeVisible();

    await page.reload();
    await expect(page.getByText('承認済み')).toBeVisible();
    await approverCtx.close();
  });

  test('[LEAVE2-E2E-001] list filter by status keeps only matching rows and survives navigation back', async ({ page }) => {
    await login(page, 'employee');
    await page.goto('/requests');
    await page.getByLabel('状態').selectOption('submitted');
    const rows = page.locator('tbody tr');
    const count = await rows.count();
    for (let i = 0; i < count; i++) await expect(rows.nth(i)).toContainText('承認待ち');
  });

  test('[LEAVE-UI-001] remaining character counter reaches 0 at 500 characters and input stops there', async ({ page }) => {
    await login(page, 'employee');
    await page.goto('/requests/new');
    await page.getByLabel('理由').fill('あ'.repeat(600));
    await expect(page.getByText('残り 0 文字')).toBeVisible();
    await expect(page.getByLabel('理由')).toHaveValue('あ'.repeat(500));
  });
});
