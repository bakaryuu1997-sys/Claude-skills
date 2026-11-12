import { Global, Module } from '@nestjs/common';
import { UsersRepository } from '../auth/users.repository';
import { CONFIG, validateAndLoadConfig } from '../config';
import { AuditService } from './audit.service';
import { CLOCK } from './clock';
import { DepartmentsRepository } from './departments.repository';

@Global()
@Module({
  providers: [
    { provide: CONFIG, useFactory: () => validateAndLoadConfig() },
    { provide: CLOCK, useValue: () => new Date() },
    AuditService,
    UsersRepository,
    DepartmentsRepository,
  ],
  exports: [CONFIG, CLOCK, AuditService, UsersRepository, DepartmentsRepository],
})
export class CoreModule {}
