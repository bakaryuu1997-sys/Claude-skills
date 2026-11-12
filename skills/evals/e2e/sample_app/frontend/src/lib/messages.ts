import { ApiError } from './api-client';

/** User-facing messages keyed by API error code (message list of the basic design, table 6-1). */
const MESSAGES: Record<string, string> = {
  'ERR-VAL-001': '入力形式が正しくありません',
  'ERR-VAL-002': '終了日は開始日以降の日付を入力してください',
  'ERR-AUTH-001': '社員番号またはパスワードが正しくありません',
  'ERR-AUTH-002': 'アカウントがロックされています',
  'ERR-AUTH-003': 'ログインの有効期限が切れました。再度ログインしてください',
  'ERR-LEAVE-001': '同じ期間に申請が存在します',
  'ERR-LEAVE-002': '残業は事前承認が必要です',
  'ERR-APPR-001': 'この申請を承認・差戻しする権限がありません',
  'ERR-APPR-002': '申請の状態が変更されました。画面を更新してください',
  'ERR-SYS-404': '対象が見つかりません',
  'ERR-SYS-429': '操作が多すぎます。しばらくしてから再度お試しください',
  'ERR-SYS-500': 'システムエラーが発生しました。時間をおいて再度お試しください',
  'ERR-NET-000': '通信に失敗しました。ネットワークを確認してください',
};

export function messageFor(err: unknown): string {
  if (err instanceof ApiError) return MESSAGES[err.code] ?? MESSAGES['ERR-SYS-500'];
  return MESSAGES['ERR-NET-000'];
}

/** Support reference shown next to server errors so users can report it. */
export function requestIdOf(err: unknown): string | undefined {
  return err instanceof ApiError && err.requestId ? err.requestId : undefined;
}

/** Map error.details[].field to a per-field message for inline display. */
export function fieldErrors(err: unknown): Record<string, string> {
  if (!(err instanceof ApiError) || !err.details) return {};
  return Object.fromEntries(err.details.map((d) => [d.field, MESSAGES[err.code] ?? d.issue]));
}
