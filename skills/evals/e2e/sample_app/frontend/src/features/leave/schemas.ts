import { z } from 'zod';

const DATE = /^\d{4}-\d{2}-\d{2}$/;

/** Mirrors the backend validation: dateTo >= dateFrom, hours 0-24 with 2 decimals, reason <= 500 characters. */
export const createLeaveSchema = z
  .object({
    type: z.string().min(1, '休暇種別を選択してください'),
    dateFrom: z.string().regex(DATE, '日付を入力してください'),
    dateTo: z.string().regex(DATE, '日付を入力してください'),
    hours: z
      .number()
      .min(0, '0〜24 の範囲で入力してください')
      .max(24, '0〜24 の範囲で入力してください')
      .refine((v) => Math.abs(v * 100 - Math.round(v * 100)) < 1e-9, '小数2桁までです')
      .optional(),
    reason: z.string().max(500, '500文字以内で入力してください'),
  })
  .superRefine((v, ctx) => {
    if (v.dateFrom && v.dateTo && v.dateTo < v.dateFrom) {
      ctx.addIssue({ code: 'custom', path: ['dateTo'], message: '終了日は開始日以降の日付を入力してください' });
    }
    if (v.type === 'OVERTIME' && v.hours === undefined) {
      ctx.addIssue({ code: 'custom', path: ['hours'], message: '残業時間を入力してください' });
    }
  });

export type CreateLeaveInput = z.infer<typeof createLeaveSchema>;

export const loginSchema = z.object({
  employeeId: z.string().regex(/^\d{6}$/, '社員番号は半角数字6桁で入力してください'),
  password: z.string().min(12, 'パスワードは12文字以上で入力してください'),
});

export const delegationSchema = z
  .object({
    delegateId: z.string().uuid('代理者のIDを入力してください'),
    validFrom: z.string().regex(DATE, '日付を入力してください'),
    validTo: z.string().regex(DATE, '日付を入力してください'),
  })
  .refine((v) => v.validTo >= v.validFrom, { path: ['validTo'], message: '終了日は開始日以降の日付を入力してください' });

export const rejectSchema = z.object({
  reason: z.string().min(1, '差戻し理由を入力してください').max(500, '500文字以内で入力してください'),
});
