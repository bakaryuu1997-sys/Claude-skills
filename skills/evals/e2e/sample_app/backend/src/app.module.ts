import { Module } from '@nestjs/common';
import { ApprovalModule } from './approval/approval.module';
import { AuthModule } from './auth/auth.module';
import { CoreModule } from './common/core.module';
import { HealthController } from './health.controller';
import { LeaveModule } from './leave/leave.module';
import { ReportModule } from './report/report.module';

@Module({
  imports: [CoreModule, AuthModule, LeaveModule, ApprovalModule, ReportModule],
  controllers: [HealthController],
})
export class AppModule {}
