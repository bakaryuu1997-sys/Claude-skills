import { expect, test } from '@playwright/test';
import { login } from './helpers';

test.describe('AUTH', () => {
  test('[AUTH-E2E-001] employee logs in, lands on the request list, and cannot reopen it after logout', async ({ page }) => {
    await login(page, 'employee');
    await expect(page).toHaveURL(/\/requests$/);
    await expect(page.getByRole('heading', { name: '申請一覧' })).toBeVisible();

    await page.getByRole('button', { name: 'ログアウト' }).click();
    await expect(page).toHaveURL(/\/login/);

    await page.goto('/requests');
    // the list API answers 401 without a session, so no data is shown and the user is sent to the login screen
    await expect(page).toHaveURL(/\/login/);
  });

  test('[AUTH-UI-001] NEW client-side validation shows messages under the fields', async ({ page }) => {
    await page.goto('/login');
    await page.getByLabel('社員番号').fill('12A456');
    await page.getByLabel('パスワード').fill('short');
    await page.getByRole('button', { name: 'ログイン' }).click();
    await expect(page.getByText('社員番号は半角数字6桁で入力してください')).toBeVisible();
    await expect(page.getByText('パスワードは12文字以上で入力してください')).toBeVisible();
  });
});
