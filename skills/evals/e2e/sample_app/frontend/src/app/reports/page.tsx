'use client';

import { useMutation } from '@tanstack/react-query';
import { useState } from 'react';
import { z } from 'zod';
import { AppShell } from '@/components/app-shell';
import { apiDownload } from '@/lib/api-client';
import { messageFor } from '@/lib/messages';

const schema = z.object({
  departmentId: z.string().uuid('部門IDを入力してください'),
  yearMonth: z.string().regex(/^\d{4}-(0[1-9]|1[0-2])$/, '年月は YYYY-MM 形式で入力してください'),
});

export default function ReportPage() {
  const [departmentId, setDepartmentId] = useState('');
  const [yearMonth, setYearMonth] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [banner, setBanner] = useState<string | null>(null);

  const download = useMutation({
    mutationFn: async (q: { departmentId: string; yearMonth: string }) => {
      const blob = await apiDownload(`/reports/monthly-attendance.csv?${new URLSearchParams(q).toString()}`);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `monthly-attendance-${q.yearMonth}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    },
  });

  const submit = () => {
    setBanner(null);
    const parsed = schema.safeParse({ departmentId, yearMonth });
    if (!parsed.success) {
      setErrors(Object.fromEntries(parsed.error.issues.map((i) => [String(i.path[0]), i.message])));
      return;
    }
    setErrors({});
    download.mutate(parsed.data, { onError: (err) => setBanner(messageFor(err)) });
  };

  return (
    <AppShell title="月次勤怠CSV出力">
      <form className="max-w-xl space-y-4" noValidate onSubmit={(e) => e.preventDefault()}>
        <div>
          <label htmlFor="departmentId">部門ID</label>
          <input id="departmentId" className="field" value={departmentId} onChange={(e) => setDepartmentId(e.target.value)} aria-invalid={!!errors.departmentId} />
          {errors.departmentId && <p className="err">{errors.departmentId}</p>}
        </div>
        <div>
          <label htmlFor="yearMonth">対象年月（YYYY-MM）</label>
          <input id="yearMonth" className="field" placeholder="2027-02" value={yearMonth} onChange={(e) => setYearMonth(e.target.value)} aria-invalid={!!errors.yearMonth} />
          {errors.yearMonth && <p className="err">{errors.yearMonth}</p>}
        </div>
        {banner && <p role="alert" className="err">{banner}</p>}
        <button type="button" className="btn btn-primary" disabled={download.isPending} onClick={submit}>
          {download.isPending ? '出力中…' : 'CSVをダウンロード'}
        </button>
      </form>
    </AppShell>
  );
}
