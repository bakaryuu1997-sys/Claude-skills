import { Body, Controller, HttpCode, Param, ParseUUIDPipe, Post, Put, Req, UseGuards } from '@nestjs/common';
import { AuthGuard, MinRole, type AuthedRequest } from '../common/auth.guard';
import { ApproveDto, DelegationDto, RejectDto } from './approval.dto';
import { ApprovalService } from './approval.service';

@Controller()
@UseGuards(AuthGuard)
@MinRole('manager')
export class ApprovalController {
  constructor(private readonly service: ApprovalService) {}

  @Post('leave-requests/:id/approve')
  @HttpCode(200)
  approve(@Req() req: AuthedRequest, @Param('id', ParseUUIDPipe) id: string, @Body() dto: ApproveDto) {
    return this.service.approve(req.user, id, dto.comment);
  }

  @Post('leave-requests/:id/reject')
  @HttpCode(200)
  reject(@Req() req: AuthedRequest, @Param('id', ParseUUIDPipe) id: string, @Body() dto: RejectDto) {
    return this.service.reject(req.user, id, dto.reason);
  }

  @Put('approver-delegations')
  setDelegation(@Req() req: AuthedRequest, @Body() dto: DelegationDto) {
    const d = this.service.setDelegation(req.user, dto.delegateId, dto.validFrom, dto.validTo);
    return { id: d.id, delegateId: d.delegateId, validFrom: d.validFrom, validTo: d.validTo };
  }
}
