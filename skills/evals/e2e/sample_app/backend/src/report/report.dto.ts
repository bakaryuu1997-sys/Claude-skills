import { IsUUID, Matches } from 'class-validator';

export class MonthlyReportQueryDto {
  @IsUUID()
  departmentId!: string;

  @Matches(/^\d{4}-(0[1-9]|1[0-2])$/, { message: 'yearMonth must be YYYY-MM with month 01-12' })
  yearMonth!: string;
}
