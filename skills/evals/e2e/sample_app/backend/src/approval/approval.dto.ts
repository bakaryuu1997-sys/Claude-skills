import { IsOptional, IsString, IsUUID, Matches, MaxLength, MinLength } from 'class-validator';

const DATE_PATTERN = /^\d{4}-\d{2}-\d{2}$/;

export class ApproveDto {
  @IsOptional()
  @IsString()
  @MaxLength(500)
  comment?: string;
}

export class RejectDto {
  @IsString()
  @MinLength(1)
  @MaxLength(500)
  reason!: string;
}

export class DelegationDto {
  @IsUUID()
  delegateId!: string;

  @Matches(DATE_PATTERN, { message: 'validFrom must be YYYY-MM-DD' })
  validFrom!: string;

  @Matches(DATE_PATTERN, { message: 'validTo must be YYYY-MM-DD' })
  validTo!: string;
}
