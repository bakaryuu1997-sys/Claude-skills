import {
  Body,
  Controller,
  Get,
  HttpCode,
  Param,
  ParseUUIDPipe,
  Post,
  Query,
  Req,
  UseGuards,
} from '@nestjs/common';
import { AuthGuard, type AuthedRequest } from '../common/auth.guard';
import { CreateLeaveRequestDto, ListQueryDto } from './leave.dto';
import { LeaveService } from './leave.service';

@Controller('leave-requests')
@UseGuards(AuthGuard)
export class LeaveController {
  constructor(private readonly service: LeaveService) {}

  @Post()
  @HttpCode(201)
  create(@Req() req: AuthedRequest, @Body() dto: CreateLeaveRequestDto) {
    const r = this.service.create(req.user, dto);
    return { id: r.id, status: r.status, createdAt: r.createdAt };
  }

  @Get()
  list(@Req() req: AuthedRequest, @Query() q: ListQueryDto) {
    return this.service.list(req.user, q);
  }

  @Get(':id')
  get(@Req() req: AuthedRequest, @Param('id', ParseUUIDPipe) id: string) {
    const r = this.service.get(req.user, id);
    return {
      id: r.id,
      type: r.type,
      dateFrom: r.dateFrom,
      dateTo: r.dateTo,
      hours: r.hours,
      reason: r.reason,
      status: r.status,
      steps: r.steps,
    };
  }
}
