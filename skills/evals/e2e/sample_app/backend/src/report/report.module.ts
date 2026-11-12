import { Module } from '@nestjs/common';
import { LeaveModule } from '../leave/leave.module';
import { ReportController } from './report.controller';
import { ReportService } from './report.service';

@Module({
  imports: [LeaveModule],
  controllers: [ReportController],
  providers: [ReportService],
})
export class ReportModule {}
