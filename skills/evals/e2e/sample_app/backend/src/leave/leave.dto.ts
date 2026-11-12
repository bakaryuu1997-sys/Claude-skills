import { Type } from 'class-transformer';
import {
  IsBoolean,
  IsIn,
  IsInt,
  IsNumber,
  IsOptional,
  IsString,
  Matches,
  Max,
  MaxLength,
  Min,
  MinLength,
} from 'class-validator';

const DATE_PATTERN = /^\d{4}-\d{2}-\d{2}$/;

export class CreateLeaveRequestDto {
  @IsString()
  @MinLength(1)
  type!: string;

  @Matches(DATE_PATTERN, { message: 'dateFrom must be YYYY-MM-DD' })
  dateFrom!: string;

  @Matches(DATE_PATTERN, { message: 'dateTo must be YYYY-MM-DD' })
  dateTo!: string;

  @IsOptional()
  @IsNumber({ maxDecimalPlaces: 2 })
  @Min(0)
  @Max(24)
  hours?: number;

  @IsString()
  @MaxLength(500)
  reason!: string;

  /** true = submit, false = save as draft */
  @IsBoolean()
  submit!: boolean;
}

export class ListQueryDto {
  @IsOptional()
  @IsIn(['draft', 'submitted', 'approved', 'rejected'])
  status?: string;

  @IsOptional()
  @Matches(DATE_PATTERN, { message: 'from must be YYYY-MM-DD' })
  from?: string;

  @IsOptional()
  @Matches(DATE_PATTERN, { message: 'to must be YYYY-MM-DD' })
  to?: string;

  @IsOptional()
  @Type(() => Number)
  @IsInt()
  @Min(1)
  page?: number;

  @IsOptional()
  @Type(() => Number)
  @IsInt()
  @Min(1)
  @Max(100)
  pageSize?: number;
}
