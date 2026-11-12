import { expect, type Page } from '@playwright/test';

/** Test accounts come from the environment of the seeded backend; no credentials live in the repository. */
export function account(role: 'employee' | 'manager' | 'hr'): { id: string; password: string } {
  const key = role.toUpperCase();
  const id = process.env[`E2E_${key}_ID`];
  const password = process.env[`E2E_${key}_PASSWORD`];
  if (!id || !password) throw new Error(`Set E2E_${key}_ID and E2E_${key}_PASSWORD for the seeded test account`);
  return { id, password };
}

/** A random future date so reruns never collide with the overlap rule. */
export function futureDate(): string {
  const d = new Date(Date.UTC(2030, 0, 1) + Math.floor(Math.random() * 3000) * 86_400_000);
  return d.toISOString().slice(0, 10);
}

export async function login(page: Page, role: 'employee' | 'manager' | 'hr'): Promise<void> {
  const { id, password } = account(role);
  await page.goto('/login');
  await page.getByLabel('社員番号').fill(id);
  await page.getByLabel('パスワード').fill(password);
  await page.getByRole('button', { name: 'ログイン' }).click();
  await expect(page).not.toHaveURL(/\/login/);
}
