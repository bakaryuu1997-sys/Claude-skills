// The leave type list is configuration, not mock data: the API design has no master-data endpoint yet
// (see the implementation report, open item "leave type master"). Keep in sync with the backend master.
export const LEAVE_TYPES = [
  { code: 'ANNUAL', label: '年次有給休暇' },
  { code: 'SICK', label: '病気休暇' },
  { code: 'SPECIAL', label: '特別休暇' },
  { code: 'OVERTIME_PRE', label: '残業の事前申請' },
  { code: 'OVERTIME', label: '残業' },
] as const;

export const STATUS_LABELS: Record<string, string> = {
  draft: '下書き',
  submitted: '承認待ち',
  approved: '承認済み',
  rejected: '差戻し',
};
