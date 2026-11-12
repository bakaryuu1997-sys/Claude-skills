import { Controller, Get, Header, Query, StreamableFile, UseGuards } from '@nestjs/common';
import { AuthGuard, MinRole } from '../common/auth.guard';
import { MonthlyReportQueryDto } from './report.dto';
import { ReportService } from './report.service';

@Controller('reports')
@UseGuards(AuthGuard)
@MinRole('hr')
export class ReportController {
  constructor(private readonly service: ReportService) {}

  @Get('monthly-attendance.csv')
  @Header('Content-Type', 'text/csv; charset=Shift_JIS')
  monthly(@Query() q: MonthlyReportQueryDto): StreamableFile {
    return new StreamableFile(this.service.monthlyCsv(q.departmentId, q.yearMonth));
  }
}
