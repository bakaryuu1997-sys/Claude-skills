import { Module } from '@nestjs/common';
import { LeaveController } from './leave.controller';
import { LeaveRepository } from './leave.repository';
import { LeaveService } from './leave.service';

@Module({
  controllers: [LeaveController],
  providers: [LeaveRepository, LeaveService],
  exports: [LeaveRepository, LeaveService],
})
export class LeaveModule {}
